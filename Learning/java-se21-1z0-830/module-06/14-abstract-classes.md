# Abstract Classes and Methods

## Introduction

Abstract classes are a fundamental part of Java's approach to abstraction—one of the four pillars of Object-Oriented Programming. An abstract class serves as a blueprint for other classes, defining common structure and behavior while leaving specific implementations to subclasses. Abstract classes allow you to create hierarchies where parent classes define the "what" and child classes define the "how."

## What are Abstract Classes?

An abstract class is a class declared with the `abstract` keyword that cannot be instantiated directly. It may contain both abstract methods (methods without implementation) and concrete methods (methods with implementation).

### Syntax

```java
abstract class ClassName {
    // Abstract method (no body)
    abstract returnType methodName(parameters);
    
    // Concrete method (with body)
    returnType concreteMethod(parameters) {
        // implementation
    }
}
```

### Basic Example

```java
abstract class Animal {
    // Abstract method - no implementation
    abstract void makeSound();
    
    // Concrete method - has implementation
    void breathe() {
        System.out.println("Breathing...");
    }
}

class Dog extends Animal {
    // Must implement all abstract methods
    @Override
    void makeSound() {
        System.out.println("Bark bark!");
    }
}

public class AbstractDemo {
    public static void main(String[] args) {
        // Animal animal = new Animal();  // ERROR: Cannot instantiate abstract class
        
        Animal dog = new Dog();  // OK: Can reference subclass through abstract type
        dog.makeSound();  // Output: Bark bark!
        dog.breathe();    // Output: Breathing...
    }
}
```

## Key Characteristics of Abstract Classes

### 1. Cannot Be Instantiated

```java
abstract class Shape {
    abstract double area();
}

public class Test {
    public static void main(String[] args) {
        // Shape shape = new Shape();  // Compilation error!
    }
}
```

### 2. Can Have Constructors

Despite not being instantiable, abstract classes can have constructors that are called when subclasses are instantiated.

```java
abstract class Vehicle {
    private String brand;
    
    // Constructor in abstract class
    Vehicle(String brand) {
        this.brand = brand;
        System.out.println("Vehicle constructor called");
    }
    
    String getBrand() {
        return brand;
    }
    
    abstract void start();
}

class Car extends Vehicle {
    Car(String brand) {
        super(brand);  // Must call parent constructor
        System.out.println("Car constructor called");
    }
    
    @Override
    void start() {
        System.out.println(getBrand() + " car is starting");
    }
}

public class ConstructorDemo {
    public static void main(String[] args) {
        Car car = new Car("Toyota");
        // Output:
        // Vehicle constructor called
        // Car constructor called
        car.start();  // Output: Toyota car is starting
    }
}
```

### 3. Can Have Instance Variables and Methods

```java
abstract class Employee {
    private String name;
    private double baseSalary;
    
    Employee(String name, double baseSalary) {
        this.name = name;
        this.baseSalary = baseSalary;
    }
    
    // Concrete method
    String getName() {
        return name;
    }
    
    // Concrete method
    double getBaseSalary() {
        return baseSalary;
    }
    
    // Abstract method - each employee type calculates bonus differently
    abstract double calculateBonus();
    
    // Concrete method using abstract method (Template Method pattern)
    final double getTotalCompensation() {
        return baseSalary + calculateBonus();
    }
}

class Manager extends Employee {
    Manager(String name, double baseSalary) {
        super(name, baseSalary);
    }
    
    @Override
    double calculateBonus() {
        return getBaseSalary() * 0.20;  // 20% bonus
    }
}

class Developer extends Employee {
    Developer(String name, double baseSalary) {
        super(name, baseSalary);
    }
    
    @Override
    double calculateBonus() {
        return getBaseSalary() * 0.15;  // 15% bonus
    }
}
```

### 4. Can Have Static Methods

```java
abstract class MathOperations {
    // Static method in abstract class
    static int add(int a, int b) {
        return a + b;
    }
    
    // Abstract method
    abstract int calculate(int a, int b);
}

class Multiply extends MathOperations {
    @Override
    int calculate(int a, int b) {
        return a * b;
    }
}

public class StaticMethodDemo {
    public static void main(String[] args) {
        // Can call static method without instantiation
        int sum = MathOperations.add(5, 3);  // OK
        System.out.println("Sum: " + sum);
        
        MathOperations op = new Multiply();
        System.out.println("Product: " + op.calculate(5, 3));
    }
}
```

## Abstract Methods

### Rules for Abstract Methods

1. **Must be declared with `abstract` keyword**
2. **Cannot have a body** (no implementation)
3. **Must be implemented by first concrete subclass**
4. **Cannot be static, final, or private**
5. **Can have any access modifier except private**

```java
abstract class Rules {
    // Valid abstract methods
    abstract void method1();
    protected abstract void method2();
    public abstract String method3();
    
    // INVALID abstract methods
    // private abstract void method4();  // ERROR: abstract method cannot be private
    // static abstract void method5();   // ERROR: abstract method cannot be static
    // final abstract void method6();    // ERROR: abstract method cannot be final
    // abstract void method7() { }       // ERROR: abstract method cannot have body
}
```

### Implementing Abstract Methods

```java
abstract class Shape {
    abstract double area();
    abstract double perimeter();
}

class Circle extends Shape {
    private double radius;
    
    Circle(double radius) {
        this.radius = radius;
    }
    
    @Override
    double area() {
        return Math.PI * radius * radius;
    }
    
    @Override
    double perimeter() {
        return 2 * Math.PI * radius;
    }
}

class Rectangle extends Shape {
    private double length, width;
    
    Rectangle(double length, double width) {
        this.length = length;
        this.width = width;
    }
    
    @Override
    double area() {
        return length * width;
    }
    
    @Override
    double perimeter() {
        return 2 * (length + width);
    }
}
```

## Abstract Classes vs Concrete Classes

### When to Use Abstract Classes

Use abstract classes when:
1. You want to share code among closely related classes
2. You expect classes extending your abstract class to have common methods or fields
3. You want to declare non-static, non-final fields
4. You want to provide default implementation for some methods

### When to Use Concrete Classes

Use concrete classes when:
1. The class represents a complete, instantiable entity
2. All methods have meaningful default implementations
3. No forced structure is needed for subclasses

## Multiple Levels of Abstraction

```java
abstract class LivingThing {
    abstract void reproduce();
    
    void grow() {
        System.out.println("Growing...");
    }
}

abstract class Animal extends LivingThing {
    // Inherits abstract method reproduce()
    abstract void move();
    
    // Concrete implementation
    void breathe() {
        System.out.println("Breathing oxygen");
    }
}

abstract class Mammal extends Animal {
    // Inherits abstract methods: reproduce(), move()
    
    // Implements one abstract method
    @Override
    void reproduce() {
        System.out.println("Giving birth to live young");
    }
    
    // Still abstract - doesn't implement move()
}

class Dog extends Mammal {
    // Must implement all remaining abstract methods
    @Override
    void move() {
        System.out.println("Walking on four legs");
    }
}

public class AbstractionHierarchy {
    public static void main(String[] args) {
        Dog dog = new Dog();
        dog.grow();       // From LivingThing
        dog.breathe();    // From Animal
        dog.reproduce();  // From Mammal
        dog.move();       // From Dog
    }
}
```

## Template Method Pattern

Abstract classes are perfect for the Template Method design pattern, where the abstract class defines the skeleton of an algorithm.

```java
abstract class DataProcessor {
    // Template method - defines the algorithm structure
    public final void process() {
        readData();
        processData();
        writeData();
    }
    
    // Concrete method - same for all processors
    void readData() {
        System.out.println("Reading data from source");
    }
    
    // Abstract method - varies by processor type
    abstract void processData();
    
    // Concrete method with default implementation
    // Can be overridden if needed
    void writeData() {
        System.out.println("Writing data to destination");
    }
}

class CSVProcessor extends DataProcessor {
    @Override
    void processData() {
        System.out.println("Processing CSV data");
    }
}

class XMLProcessor extends DataProcessor {
    @Override
    void processData() {
        System.out.println("Processing XML data");
    }
    
    @Override
    void writeData() {
        System.out.println("Writing XML data with schema validation");
    }
}

public class TemplateMethodDemo {
    public static void main(String[] args) {
        DataProcessor csvProcessor = new CSVProcessor();
        csvProcessor.process();
        
        System.out.println();
        
        DataProcessor xmlProcessor = new XMLProcessor();
        xmlProcessor.process();
    }
}
```

## Abstract Classes with Interfaces

Abstract classes can implement interfaces, and they don't have to implement all interface methods.

```java
interface Drawable {
    void draw();
    void resize(double factor);
}

abstract class Shape implements Drawable {
    protected String color;
    
    Shape(String color) {
        this.color = color;
    }
    
    // Implements one interface method
    @Override
    public void resize(double factor) {
        System.out.println("Resizing by factor: " + factor);
    }
    
    // Doesn't implement draw() - leaves it abstract
    // Subclasses must implement it
    
    abstract double area();
}

class Circle extends Shape {
    private double radius;
    
    Circle(String color, double radius) {
        super(color);
        this.radius = radius;
    }
    
    @Override
    public void draw() {
        System.out.println("Drawing " + color + " circle");
    }
    
    @Override
    double area() {
        return Math.PI * radius * radius;
    }
}
```

## Common Mistakes and Best Practices

### Mistake 1: Forgetting to Implement Abstract Methods

```java
abstract class Animal {
    abstract void makeSound();
    abstract void move();
}

// ERROR: Missing implementation of move()
class Dog extends Animal {
    @Override
    void makeSound() {
        System.out.println("Bark");
    }
    // Compilation error: Dog is not abstract and does not override move()
}
```

**Fix**: Either implement all abstract methods or make the subclass abstract too.

```java
// Option 1: Implement all methods
class Dog extends Animal {
    @Override
    void makeSound() {
        System.out.println("Bark");
    }
    
    @Override
    void move() {
        System.out.println("Walk");
    }
}

// Option 2: Make subclass abstract
abstract class Dog extends Animal {
    @Override
    void makeSound() {
        System.out.println("Bark");
    }
    // Still abstract - doesn't implement move()
}
```

### Mistake 2: Making Abstract Methods Private

```java
abstract class Wrong {
    // ERROR: abstract methods cannot be private
    // private abstract void method();
}
```

**Explanation**: Abstract methods must be accessible to subclasses to be overridden.

### Mistake 3: Making Abstract Methods Final or Static

```java
abstract class Wrong {
    // ERROR: abstract methods cannot be final
    // final abstract void method1();
    
    // ERROR: abstract methods cannot be static
    // static abstract void method2();
}
```

**Explanation**: Final methods cannot be overridden, and static methods belong to the class, not instances. Both conflict with the purpose of abstract methods.

## Abstract Classes vs Interfaces

| Feature | Abstract Class | Interface |
|---------|---------------|-----------|
| Methods | Can have abstract and concrete methods | All methods are implicitly abstract (pre-Java 8); can have default/static methods (Java 8+) |
| Variables | Can have instance variables (any access modifier) | Only public static final constants |
| Constructor | Can have constructors | Cannot have constructors |
| Access Modifiers | Methods can have any access modifier | Methods are implicitly public |
| Multiple Inheritance | A class can extend only one abstract class | A class can implement multiple interfaces |
| When to Use | When classes share code and have IS-A relationship | When defining contracts for unrelated classes |

```java
// Abstract class - common code for related classes
abstract class Vehicle {
    protected String brand;
    protected int year;
    
    Vehicle(String brand, int year) {
        this.brand = brand;
        this.year = year;
    }
    
    abstract void start();
    
    void displayInfo() {
        System.out.println(year + " " + brand);
    }
}

// Interface - contract for behavior
interface Electric {
    void charge();
    int getBatteryLevel();
}

// Can extend abstract class AND implement interface
class ElectricCar extends Vehicle implements Electric {
    private int batteryLevel;
    
    ElectricCar(String brand, int year) {
        super(brand, year);
        this.batteryLevel = 100;
    }
    
    @Override
    void start() {
        if (batteryLevel > 0) {
            System.out.println("Electric car starting silently");
        } else {
            System.out.println("Battery depleted!");
        }
    }
    
    @Override
    public void charge() {
        batteryLevel = 100;
        System.out.println("Charging complete");
    }
    
    @Override
    public int getBatteryLevel() {
        return batteryLevel;
    }
}
```

## Summary

- **Abstract classes** cannot be instantiated and serve as blueprints for concrete subclasses
- Use the `abstract` keyword to declare abstract classes and methods
- Abstract methods have no implementation and must be implemented by concrete subclasses
- Abstract classes can have constructors, instance variables, and concrete methods
- A class can extend only one abstract class (single inheritance)
- Abstract classes are ideal for sharing code among related classes
- Use abstract classes when you have an IS-A relationship and want to provide common functionality
- The Template Method pattern leverages abstract classes effectively
- Abstract methods cannot be private, static, or final
- A subclass must either implement all abstract methods or be declared abstract itself
