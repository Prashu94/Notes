# Module 5.1: Classes and Objects

## 📚 Table of Contents
1. [Introduction to OOP](#introduction-to-oop)
2. [Classes](#classes)
3. [Objects](#objects)
4. [Constructors](#constructors)
5. [Instance vs Static Members](#instance-vs-static-members)
6. [Access Modifiers](#access-modifiers)
7. [The `this` Keyword](#the-this-keyword)
8. [Object Initialization](#object-initialization)
9. [Best Practices](#best-practices)
10. [Common Pitfalls](#common-pitfalls)

---

## Introduction to OOP

Object-Oriented Programming (OOP) is a programming paradigm based on objects that contain data (fields) and code (methods).

### Four Pillars of OOP

1. **Encapsulation** - Bundling data and methods, hiding internal details
2. **Inheritance** - Creating new classes from existing ones
3. **Polymorphism** - Objects taking multiple forms
4. **Abstraction** - Hiding complex implementation details

---

## Classes

A class is a blueprint or template for creating objects. It defines the structure and behavior.

### Basic Class Declaration

```java
public class Car {
    // Fields (instance variables)
    String brand;
    String model;
    int year;
    
    // Methods
    void start() {
        System.out.println("Car is starting");
    }
    
    void stop() {
        System.out.println("Car is stopping");
    }
}
```

### Class Components

```java
public class Person {
    // 1. Fields (instance variables)
    private String name;
    private int age;
    
    // 2. Constructor
    public Person(String name, int age) {
        this.name = name;
        this.age = age;
    }
    
    // 3. Methods
    public void introduce() {
        System.out.println("I'm " + name + ", " + age + " years old");
    }
    
    // 4. Getters/Setters
    public String getName() {
        return name;
    }
    
    public void setName(String name) {
        this.name = name;
    }
}
```

---

## Objects

An object is an instance of a class. It has state (field values) and behavior (methods).

### Creating Objects

```java
// Using new keyword
Car myCar = new Car();
Car yourCar = new Car();

// Each object has its own copy of instance variables
myCar.brand = "Toyota";
myCar.model = "Camry";
myCar.year = 2024;

yourCar.brand = "Honda";
yourCar.model = "Accord";
yourCar.year = 2023;
```

### Accessing Members

```java
public class Rectangle {
    int width;
    int height;
    
    int area() {
        return width * height;
    }
}

// Create object
Rectangle rect = new Rectangle();

// Access fields
rect.width = 10;
rect.height = 5;

// Call methods
int area = rect.area();  // 50
```

### Object References

```java
Car car1 = new Car();
car1.brand = "Tesla";

Car car2 = car1;  // car2 references the same object
car2.brand = "Ford";

System.out.println(car1.brand);  // Ford (both point to same object)

// Null reference
Car car3 = null;  // No object created
// car3.start();  // NullPointerException
```

---

## Constructors

Constructors initialize objects when they're created.

### Default Constructor

```java
public class Book {
    String title;
    String author;
    
    // No constructor defined - Java provides default constructor
}

Book book = new Book();  // Uses default constructor
```

### Parameterized Constructor

```java
public class Book {
    String title;
    String author;
    
    // Constructor with parameters
    public Book(String title, String author) {
        this.title = title;
        this.author = author;
    }
}

Book book = new Book("1984", "George Orwell");
```

### Constructor Overloading

```java
public class Employee {
    String name;
    int age;
    double salary;
    
    // No-arg constructor
    public Employee() {
        this.name = "Unknown";
        this.age = 0;
        this.salary = 0.0;
    }
    
    // Constructor with name only
    public Employee(String name) {
        this.name = name;
        this.age = 0;
        this.salary = 0.0;
    }
    
    // Constructor with all parameters
    public Employee(String name, int age, double salary) {
        this.name = name;
        this.age = age;
        this.salary = salary;
    }
}

Employee e1 = new Employee();
Employee e2 = new Employee("Alice");
Employee e3 = new Employee("Bob", 30, 50000.0);
```

### Constructor Chaining with `this()`

```java
public class Product {
    String name;
    double price;
    int quantity;
    
    public Product(String name) {
        this(name, 0.0);  // Call constructor with 2 params
    }
    
    public Product(String name, double price) {
        this(name, price, 0);  // Call constructor with 3 params
    }
    
    public Product(String name, double price, int quantity) {
        this.name = name;
        this.price = price;
        this.quantity = quantity;
    }
}
```

### Constructor Rules

1. Constructor name must match class name
2. No return type (not even void)
3. `this()` must be first statement if used
4. If no constructor is defined, Java provides default
5. If you define any constructor, default is NOT provided

---

## Instance vs Static Members

### Instance Members

Belong to each object individually.

```java
public class Counter {
    // Instance variable - each object has its own copy
    int count = 0;
    
    // Instance method - operates on specific object
    void increment() {
        count++;
    }
}

Counter c1 = new Counter();
Counter c2 = new Counter();

c1.increment();
c1.increment();
c2.increment();

System.out.println(c1.count);  // 2
System.out.println(c2.count);  // 1
```

### Static Members

Belong to the class, shared by all objects.

```java
public class BankAccount {
    // Static variable - shared by all objects
    static double interestRate = 0.05;
    
    // Instance variable - unique to each object
    double balance;
    
    // Static method - belongs to class
    static void setInterestRate(double rate) {
        interestRate = rate;
    }
    
    // Instance method - operates on specific object
    void applyInterest() {
        balance += balance * interestRate;
    }
}

// Access static members via class name
BankAccount.setInterestRate(0.06);
System.out.println(BankAccount.interestRate);  // 0.06

// All objects share the static variable
BankAccount account1 = new BankAccount();
BankAccount account2 = new BankAccount();
account1.balance = 1000;
account2.balance = 2000;

account1.applyInterest();
account2.applyInterest();

System.out.println(account1.balance);  // 1060.0
System.out.println(account2.balance);  // 2120.0
```

### Static Blocks

```java
public class Database {
    static String connectionString;
    
    // Static block - executed once when class is loaded
    static {
        connectionString = "jdbc:mysql://localhost:3306/mydb";
        System.out.println("Database initialized");
    }
    
    static void connect() {
        System.out.println("Connecting to " + connectionString);
    }
}

Database.connect();  // Prints: Database initialized, then: Connecting to...
```

### Instance vs Static Comparison

| Feature | Instance | Static |
|---------|----------|--------|
| **Belongs to** | Object | Class |
| **Access** | Via object reference | Via class name |
| **Copy** | Each object has its own | One copy shared by all |
| **this/super** | Can use | Cannot use |
| **Access static** | Yes | Yes |
| **Access instance** | Yes | No (unless via object) |

---

## Access Modifiers

Control visibility of class members.

### Four Access Levels

```java
public class AccessExample {
    public int publicField;        // Accessible everywhere
    protected int protectedField;  // Accessible in package and subclasses
    int defaultField;              // Accessible in package only (no modifier)
    private int privateField;      // Accessible only within class
    
    public void publicMethod() {}
    protected void protectedMethod() {}
    void defaultMethod() {}
    private void privateMethod() {}
}
```

### Access Level Summary

| Modifier | Same Class | Same Package | Subclass | Everywhere |
|----------|------------|--------------|----------|------------|
| **public** | ✅ | ✅ | ✅ | ✅ |
| **protected** | ✅ | ✅ | ✅ | ❌ |
| **default** | ✅ | ✅ | ❌ | ❌ |
| **private** | ✅ | ❌ | ❌ | ❌ |

### Encapsulation Example

```java
public class Person {
    // Private fields - hidden from outside
    private String name;
    private int age;
    
    // Public constructor
    public Person(String name, int age) {
        this.name = name;
        setAge(age);  // Use setter for validation
    }
    
    // Public getter
    public String getName() {
        return name;
    }
    
    // Public setter with validation
    public void setAge(int age) {
        if (age < 0 || age > 150) {
            throw new IllegalArgumentException("Invalid age");
        }
        this.age = age;
    }
    
    public int getAge() {
        return age;
    }
}

Person person = new Person("Alice", 25);
// person.age = -10;  // Compilation error - private field
person.setAge(30);     // OK - uses validation
```

---

## The `this` Keyword

`this` refers to the current object.

### Distinguishing Fields from Parameters

```java
public class Rectangle {
    int width;
    int height;
    
    public Rectangle(int width, int height) {
        this.width = width;    // this.width is the field
        this.height = height;  // width is the parameter
    }
}
```

### Calling Other Methods

```java
public class Calculator {
    int value;
    
    void setValue(int value) {
        this.value = value;
    }
    
    void reset() {
        this.setValue(0);  // Call another method using this
    }
}
```

### Passing Current Object

```java
public class Node {
    int data;
    Node next;
    
    void printList() {
        System.out.println(data);
        if (next != null) {
            next.printList();  // Recursive call
        }
    }
    
    Node getThis() {
        return this;  // Return current object
    }
}
```

---

## Object Initialization

### Order of Initialization

1. Static blocks (when class loads)
2. Instance blocks
3. Constructor

```java
public class InitOrder {
    static int staticVar;
    int instanceVar;
    
    // 1. Static block - runs once when class loads
    static {
        staticVar = 10;
        System.out.println("Static block");
    }
    
    // 2. Instance block - runs before constructor
    {
        instanceVar = 20;
        System.out.println("Instance block");
    }
    
    // 3. Constructor - runs last
    public InitOrder() {
        System.out.println("Constructor");
    }
}

InitOrder obj1 = new InitOrder();
// Output:
// Static block
// Instance block
// Constructor

InitOrder obj2 = new InitOrder();
// Output:
// Instance block (static block runs only once)
// Constructor
```

### Instance Initializer Blocks

```java
public class Student {
    String name;
    int grade;
    
    // Instance initializer block
    {
        grade = 1;  // Default grade
        System.out.println("Student created");
    }
    
    public Student(String name) {
        this.name = name;
    }
}
```

---

## Best Practices

### 1. Encapsulate Fields

```java
// Bad
public class Account {
    public double balance;  // Anyone can modify
}

// Good
public class Account {
    private double balance;
    
    public double getBalance() {
        return balance;
    }
    
    public void deposit(double amount) {
        if (amount > 0) {
            balance += amount;
        }
    }
}
```

### 2. Make Classes Immutable When Possible

```java
public final class Point {
    private final int x;
    private final int y;
    
    public Point(int x, int y) {
        this.x = x;
        this.y = y;
    }
    
    public int getX() { return x; }
    public int getY() { return y; }
    
    // No setters - immutable
}
```

### 3. Use Static for Utility Methods

```java
public class MathUtils {
    // Prevent instantiation
    private MathUtils() {}
    
    public static int max(int a, int b) {
        return (a > b) ? a : b;
    }
    
    public static int min(int a, int b) {
        return (a < b) ? a : b;
    }
}

int maximum = MathUtils.max(10, 20);
```

### 4. Initialize Fields Appropriately

```java
public class Order {
    private List<Item> items = new ArrayList<>();  // Initialize collection
    private String status = "PENDING";              // Meaningful default
    private LocalDateTime createdAt = LocalDateTime.now();
}
```

---

## Common Pitfalls

### 1. Forgetting `this` in Constructors

```java
// Wrong - parameters shadow fields
public class Person {
    String name;
    
    public Person(String name) {
        name = name;  // Assigns parameter to itself!
    }
}

// Correct
public class Person {
    String name;
    
    public Person(String name) {
        this.name = name;  // Assigns to field
    }
}
```

### 2. Accessing Instance from Static

```java
public class Example {
    int instanceVar = 10;
    static int staticVar = 20;
    
    static void staticMethod() {
        // System.out.println(instanceVar);  // Error - can't access instance
        System.out.println(staticVar);  // OK
    }
}
```

### 3. Modifying Static via Instance

```java
public class Counter {
    static int count = 0;
}

Counter c1 = new Counter();
c1.count = 10;  // Confusing - modifies static via instance
Counter.count = 10;  // Clear - use class name
```

### 4. Missing Default Constructor

```java
public class Account {
    public Account(String name) {
        // Parameterized constructor defined
    }
}

// Account acc = new Account();  // Error - no default constructor
Account acc = new Account("Alice");  // OK
```

---

## Summary

### Classes
- Blueprint for objects
- Contains fields and methods
- Supports encapsulation

### Objects
- Instances of classes
- Created with `new`
- Have state and behavior

### Constructors
- Initialize objects
- Same name as class
- Can be overloaded
- Use `this()` for chaining

### Static vs Instance
- **Static:** Class-level, shared
- **Instance:** Object-level, unique per object

### Access Modifiers
- **public:** Accessible everywhere
- **private:** Only within class
- **protected:** Package + subclasses
- **default:** Package only

---

## Practice Questions

Ready to test your knowledge? Proceed to [Classes and Objects Practice Questions](09-practice-questions.md)!

---

**Next:** [Practice Questions - Classes and Objects](09-practice-questions.md)  
**Previous:** [Loops and Iteration](../module-04/08-loops-iteration.md)

---

**Good luck!** ☕
