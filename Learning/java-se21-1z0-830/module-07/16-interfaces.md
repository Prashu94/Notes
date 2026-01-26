# Interfaces in Java

## Introduction

Interfaces are one of the most powerful features in Java, enabling abstraction, multiple inheritance of type, and designing flexible, maintainable systems. An interface defines a contract that classes can implement, specifying what methods a class must provide without dictating how those methods should be implemented.

## What is an Interface?

An interface is a reference type in Java that contains:
- **Abstract methods** (methods without implementation)
- **Default methods** (Java 8+)
- **Static methods** (Java 8+)
- **Private methods** (Java 9+)
- **Constants** (public static final variables)

### Basic Interface Syntax

```java
interface Drawable {
    // Abstract method (implicitly public abstract)
    void draw();
    
    // Constant (implicitly public static final)
    int MAX_SIZE = 100;
}

class Circle implements Drawable {
    @Override
    public void draw() {
        System.out.println("Drawing a circle");
    }
}
```

## Interface Characteristics

### 1. All Methods are Public

Interface methods are implicitly `public`. You can omit the keyword, but the implementing class must use `public`.

```java
interface Animal {
    void makeSound();  // Implicitly public abstract
}

class Dog implements Animal {
    // Must be public
    public void makeSound() {
        System.out.println("Bark");
    }
    
    // ERROR: Cannot reduce visibility
    // void makeSound() { }  // Compilation error!
}
```

### 2. All Variables are Constants

Fields in interfaces are implicitly `public static final`.

```java
interface Constants {
    int MAX_VALUE = 100;  // public static final
    String APP_NAME = "MyApp";  // public static final
}

public class Test {
    public static void main(String[] args) {
        System.out.println(Constants.MAX_VALUE);
        System.out.println(Constants.APP_NAME);
        
        // ERROR: Cannot modify constants
        // Constants.MAX_VALUE = 200;  // Compilation error!
    }
}
```

### 3. Cannot Be Instantiated

```java
interface Flyable {
    void fly();
}

public class Test {
    public static void main(String[] args) {
        // Flyable f = new Flyable();  // ERROR: Cannot instantiate interface
        
        // But can reference implementing classes
        Flyable bird = new Bird();  // OK if Bird implements Flyable
    }
}
```

### 4. Multiple Interface Implementation

A class can implement multiple interfaces, achieving multiple inheritance of type.

```java
interface Flyable {
    void fly();
}

interface Swimmable {
    void swim();
}

class Duck implements Flyable, Swimmable {
    @Override
    public void fly() {
        System.out.println("Duck flying");
    }
    
    @Override
    public void swim() {
        System.out.println("Duck swimming");
    }
}

public class MultipleInterfaceDemo {
    public static void main(String[] args) {
        Duck duck = new Duck();
        duck.fly();
        duck.swim();
        
        // Polymorphism with interfaces
        Flyable flyable = duck;
        Swimmable swimmable = duck;
    }
}
```

## Default Methods (Java 8+)

Default methods allow interfaces to provide method implementations. This enables adding new methods to interfaces without breaking existing implementations.

### Syntax and Usage

```java
interface Vehicle {
    // Abstract method
    void start();
    
    // Default method with implementation
    default void stop() {
        System.out.println("Vehicle stopping");
    }
    
    default void honk() {
        System.out.println("Beep beep!");
    }
}

class Car implements Vehicle {
    @Override
    public void start() {
        System.out.println("Car starting");
    }
    
    // Optional: Can override default methods
    @Override
    public void stop() {
        System.out.println("Car stopping with brakes");
    }
    
    // honk() inherited from interface
}

public class DefaultMethodDemo {
    public static void main(String[] args) {
        Car car = new Car();
        car.start();  // Car's implementation
        car.stop();   // Car's override
        car.honk();   // Inherited default method
    }
}
```

### Default Method Benefits

```java
// Library version 1.0
interface List {
    void add(Object item);
    Object get(int index);
    int size();
}

// Many classes implement this interface
class ArrayList implements List {
    // Implementation...
}

// Library version 2.0 - want to add forEach
interface List {
    void add(Object item);
    Object get(int index);
    int size();
    
    // Default method - doesn't break existing implementations!
    default void forEach(Consumer action) {
        for (int i = 0; i < size(); i++) {
            action.accept(get(i));
        }
    }
}

// Existing ArrayList still works without modification
```

### Calling Superinterface Default Methods

```java
interface Notification {
    default void send(String message) {
        System.out.println("Sending: " + message);
    }
}

interface Email extends Notification {
    @Override
    default void send(String message) {
        System.out.println("Email: " + message);
        Notification.super.send(message);  // Call superinterface default method
    }
}
```

## Static Methods in Interfaces (Java 8+)

Interfaces can contain static methods with implementations. These belong to the interface itself, not to implementing classes.

```java
interface MathOperations {
    // Abstract method
    int calculate(int a, int b);
    
    // Static method
    static int add(int a, int b) {
        return a + b;
    }
    
    static int multiply(int a, int b) {
        return a * b;
    }
}

class Calculator implements MathOperations {
    @Override
    public int calculate(int a, int b) {
        return a + b;
    }
}

public class StaticMethodDemo {
    public static void main(String[] args) {
        // Call static methods through interface name
        int sum = MathOperations.add(5, 3);
        int product = MathOperations.multiply(5, 3);
        
        System.out.println("Sum: " + sum);
        System.out.println("Product: " + product);
        
        // Static methods are NOT inherited
        Calculator calc = new Calculator();
        // calc.add(5, 3);  // ERROR: Cannot call static method through instance
    }
}
```

### Use Cases for Static Methods

```java
interface StringUtils {
    static boolean isNullOrEmpty(String str) {
        return str == null || str.isEmpty();
    }
    
    static String reverse(String str) {
        if (isNullOrEmpty(str)) {
            return str;
        }
        return new StringBuilder(str).reverse().toString();
    }
}

// Usage
public class Test {
    public static void main(String[] args) {
        String result = StringUtils.reverse("Hello");
        System.out.println(result);  // olleH
    }
}
```

## Private Methods in Interfaces (Java 9+)

Java 9 introduced private methods in interfaces to share code between default methods.

```java
interface Logger {
    // Private method for code reuse
    private String formatMessage(String level, String message) {
        return String.format("[%s] %s", level, message);
    }
    
    // Default methods using private method
    default void logInfo(String message) {
        System.out.println(formatMessage("INFO", message));
    }
    
    default void logError(String message) {
        System.err.println(formatMessage("ERROR", message));
    }
    
    // Private static method
    private static String getCurrentTimestamp() {
        return java.time.LocalDateTime.now().toString();
    }
    
    default void logWithTimestamp(String message) {
        System.out.println(getCurrentTimestamp() + " - " + message);
    }
}
```

## Interface Inheritance

Interfaces can extend other interfaces, inheriting their abstract methods.

```java
interface Animal {
    void eat();
    void sleep();
}

interface Mammal extends Animal {
    void giveBirth();
}

interface Flyable {
    void fly();
}

// Interface can extend multiple interfaces
interface Bat extends Mammal, Flyable {
    void echolocate();
}

class FruitBat implements Bat {
    public void eat() { System.out.println("Eating fruit"); }
    public void sleep() { System.out.println("Sleeping upside down"); }
    public void giveBirth() { System.out.println("Giving birth to pup"); }
    public void fly() { System.out.println("Flying"); }
    public void echolocate() { System.out.println("Using echolocation"); }
}
```

## Marker Interfaces

Marker interfaces are interfaces with no methods or fields, used to mark or tag a class.

```java
// Marker interface
interface Serializable {
    // No methods
}

class Employee implements Serializable {
    private String name;
    private int id;
    
    // Employee can now be serialized
}

// Framework can check if object is Serializable
public void saveToFile(Object obj) {
    if (obj instanceof Serializable) {
        // Perform serialization
        System.out.println("Saving object...");
    } else {
        System.out.println("Object cannot be serialized");
    }
}
```

## Functional Interfaces

A functional interface has exactly one abstract method. They're used extensively with lambda expressions (covered in detail in Module 10).

```java
@FunctionalInterface
interface Calculator {
    int calculate(int a, int b);  // Single abstract method
    
    // Can have default and static methods
    default void printResult(int a, int b) {
        System.out.println("Result: " + calculate(a, b));
    }
}

public class FunctionalInterfaceDemo {
    public static void main(String[] args) {
        // Lambda expression
        Calculator add = (a, b) -> a + b;
        Calculator multiply = (a, b) -> a * b;
        
        System.out.println(add.calculate(5, 3));      // 8
        System.out.println(multiply.calculate(5, 3)); // 15
    }
}
```

### @FunctionalInterface Annotation

```java
@FunctionalInterface
interface Printer {
    void print(String message);
    
    // ERROR: Second abstract method breaks functional interface contract
    // void printTwice(String message);  // Compilation error with @FunctionalInterface
}
```

## The Diamond Problem and Default Methods

When a class implements multiple interfaces with the same default method, ambiguity arises.

```java
interface Left {
    default void print() {
        System.out.println("Left");
    }
}

interface Right {
    default void print() {
        System.out.println("Right");
    }
}

// ERROR: Must resolve ambiguity
class Both implements Left, Right {
    // REQUIRED: Must override to resolve conflict
    @Override
    public void print() {
        // Can call either or both
        Left.super.print();
        Right.super.print();
        
        // Or provide own implementation
        System.out.println("Both");
    }
}
```

### Resolution Rules

1. **Classes win over interfaces**: If a class inherits a method from a superclass and an interface, the class method is used
2. **Subtype wins**: More specific interfaces override more general ones
3. **Must explicitly override**: If no clear winner, must override to resolve ambiguity

```java
class Parent {
    public void display() {
        System.out.println("Parent class");
    }
}

interface MyInterface {
    default void display() {
        System.out.println("Interface");
    }
}

// Rule 1: Class wins
class Child extends Parent implements MyInterface {
    // Uses Parent.display() automatically
}

// Rule 2: Subtype wins
interface General {
    default void show() {
        System.out.println("General");
    }
}

interface Specific extends General {
    @Override
    default void show() {
        System.out.println("Specific");
    }
}

class Demo implements General, Specific {
    // Uses Specific.show() automatically (more specific)
}
```

## Interfaces vs Abstract Classes

| Feature | Interface | Abstract Class |
|---------|-----------|----------------|
| Multiple inheritance | Can implement multiple interfaces | Can extend only one class |
| Method implementation | Abstract, default, static, private | Any method type |
| Fields | Only public static final | Any access modifier |
| Constructors | No | Yes |
| Access modifiers | Methods implicitly public | Any access modifier |
| When to use | Define contract for unrelated classes | Share code among related classes |

## Best Practices

### 1. Program to Interfaces, Not Implementations

```java
// Good - depends on abstraction
List<String> names = new ArrayList<>();

// Less flexible - depends on concrete type
ArrayList<String> names = new ArrayList<>();
```

### 2. Keep Interfaces Focused

```java
// Good - focused interface
interface Drawable {
    void draw();
}

// Bad - too many responsibilities
interface GraphicsObject {
    void draw();
    void save();
    void load();
    void print();
    void export();
}
```

### 3. Use Default Methods Carefully

```java
// Good - backward compatible addition
interface Collection {
    // Existing methods...
    
    default Stream stream() {
        return StreamSupport.stream(spliterator(), false);
    }
}

// Bad - overusing defaults undermines interface purpose
interface Service {
    default void method1() { /* complex logic */ }
    default void method2() { /* complex logic */ }
    default void method3() { /* complex logic */ }
    // Too much implementation in interface!
}
```

## Summary

- **Interfaces** define contracts that classes must implement
- Interface methods are implicitly **public abstract**
- Interface fields are implicitly **public static final** (constants)
- Classes can implement **multiple interfaces** (multiple inheritance of type)
- **Default methods** (Java 8+) provide implementations in interfaces
- **Static methods** (Java 8+) provide utility methods belonging to the interface
- **Private methods** (Java 9+) enable code reuse within interfaces
- **Functional interfaces** have exactly one abstract method
- **Diamond problem** resolved by explicit override when implementing conflicting default methods
- Interfaces enable **polymorphism** and **loose coupling**
- Use interfaces to define **what** without specifying **how**
