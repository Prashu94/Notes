# Java Interview Questions - Basic Concepts

## 1. What is Java and what are its main features?

**Answer:**
Java is a high-level, object-oriented, platform-independent programming language developed by Sun Microsystems (now Oracle) in 1995.

**Main Features:**
- **Platform Independent**: Write Once, Run Anywhere (WORA) - Java bytecode runs on any platform with JVM
- **Object-Oriented**: Everything is an object (except primitives)
- **Simple**: Easy to learn, similar to C++ but removes complex features like pointers
- **Secure**: No explicit pointers, programs run inside JVM sandbox
- **Robust**: Strong memory management, exception handling, garbage collection
- **Multithreaded**: Built-in support for concurrent programming
- **Architecture Neutral**: Bytecode is not specific to any processor architecture
- **Interpreted**: Bytecode is interpreted by JVM
- **High Performance**: JIT compiler improves performance
- **Distributed**: Supports networking, RMI, EJB

---

## 2. Explain JDK, JRE, and JVM

**Answer:**

**JVM (Java Virtual Machine):**
- Runtime environment that executes Java bytecode
- Platform-dependent (different for Windows, Linux, Mac)
- Provides runtime environment and interprets/compiles bytecode to machine code
- Components: Class Loader, Bytecode Verifier, Interpreter, JIT Compiler, Garbage Collector

**JRE (Java Runtime Environment):**
- JRE = JVM + Libraries + Other files
- Provides runtime environment to run Java applications
- Contains JVM, core libraries, and supporting files
- No development tools (compiler, debugger)

**JDK (Java Development Kit):**
- JDK = JRE + Development Tools
- Complete development kit for Java
- Includes compiler (javac), debugger, javadoc, jar, etc.
- Required for developing Java applications

```
JDK > JRE > JVM
```

---

## 3. What are the differences between C++ and Java?

**Answer:**

| Feature | Java | C++ |
|---------|------|-----|
| **Platform** | Platform-independent | Platform-dependent |
| **Pointers** | No explicit pointers | Supports pointers |
| **Multiple Inheritance** | Not supported (uses interfaces) | Supported |
| **Memory Management** | Automatic (Garbage Collection) | Manual (new/delete) |
| **Operator Overloading** | Not supported | Supported |
| **Goto Statement** | Not supported | Supported |
| **Virtual Keyword** | All non-static methods are virtual | Explicit virtual keyword |
| **Structures/Unions** | Not supported | Supported |
| **Thread Support** | Built-in (java.lang.Thread) | Not built-in |
| **Compilation** | Compiled to bytecode | Compiled to machine code |

---

## 4. What are data types in Java? Explain primitive and non-primitive types.

**Answer:**

**Primitive Data Types (8 types):**

1. **byte**: 8-bit signed integer (-128 to 127)
2. **short**: 16-bit signed integer (-32,768 to 32,767)
3. **int**: 32-bit signed integer (-2³¹ to 2³¹-1)
4. **long**: 64-bit signed integer (-2⁶³ to 2⁶³-1)
5. **float**: 32-bit floating point (6-7 decimal digits)
6. **double**: 64-bit floating point (15 decimal digits)
7. **char**: 16-bit Unicode character (0 to 65,535)
8. **boolean**: true or false

```java
byte b = 100;
short s = 10000;
int i = 100000;
long l = 100000L;
float f = 10.5f;
double d = 10.5;
char c = 'A';
boolean bool = true;
```

**Non-Primitive (Reference) Types:**
- Classes
- Interfaces
- Arrays
- Strings
- Enums

Non-primitive types are created by programmers and store references to objects in memory.

---

## 5. What is the difference between `==` and `.equals()`?

**Answer:**

**`==` operator:**
- Compares references (memory addresses)
- For primitives, compares values
- For objects, checks if both references point to same object

**`.equals()` method:**
- Compares content/values of objects
- Defined in Object class, can be overridden
- Default implementation in Object class uses `==`

```java
// Example
String s1 = new String("Hello");
String s2 = new String("Hello");
String s3 = s1;

System.out.println(s1 == s2);        // false (different objects)
System.out.println(s1.equals(s2));   // true (same content)
System.out.println(s1 == s3);        // true (same reference)

int a = 10, b = 10;
System.out.println(a == b);          // true (primitive comparison)
```

**Best Practice:**
- Use `==` for primitives and reference comparison
- Use `.equals()` for content comparison of objects
- Always override `.equals()` and `.hashCode()` together

---

## 6. What is the difference between String, StringBuilder, and StringBuffer?

**Answer:**

**String:**
- Immutable (cannot be changed after creation)
- Thread-safe (immutable objects are inherently thread-safe)
- Slow for concatenation (creates new object each time)
- Stored in String Pool

```java
String s = "Hello";
s = s + " World";  // Creates new String object
```

**StringBuilder:**
- Mutable (can be modified)
- Not thread-safe
- Fast for concatenation (modifies same object)
- Introduced in Java 5

```java
StringBuilder sb = new StringBuilder("Hello");
sb.append(" World");  // Modifies same object
```

**StringBuffer:**
- Mutable (can be modified)
- Thread-safe (synchronized methods)
- Slower than StringBuilder due to synchronization
- Legacy class (before Java 5)

```java
StringBuffer sbf = new StringBuffer("Hello");
sbf.append(" World");  // Thread-safe modification
```

**When to Use:**
- **String**: When value doesn't change frequently
- **StringBuilder**: Single-threaded, frequent modifications
- **StringBuffer**: Multi-threaded, frequent modifications

**Performance:** StringBuilder > StringBuffer > String (for concatenation)

---

## 7. What are access modifiers in Java?

**Answer:**

Access modifiers control the visibility and accessibility of classes, methods, and variables.

| Modifier | Class | Package | Subclass | World |
|----------|-------|---------|----------|-------|
| **public** | ✓ | ✓ | ✓ | ✓ |
| **protected** | ✓ | ✓ | ✓ | ✗ |
| **default** (no modifier) | ✓ | ✓ | ✗ | ✗ |
| **private** | ✓ | ✗ | ✗ | ✗ |

**Examples:**

```java
public class Example {
    public int publicVar;        // Accessible everywhere
    protected int protectedVar;  // Accessible in package & subclasses
    int defaultVar;              // Accessible within package only
    private int privateVar;      // Accessible within class only
    
    public void publicMethod() {}
    protected void protectedMethod() {}
    void defaultMethod() {}
    private void privateMethod() {}
}
```

**Key Points:**
- **public**: No restrictions
- **protected**: Package + inheritance
- **default**: Package level access
- **private**: Class level access only
- Top-level classes can only be public or default
- Private members not inherited by subclasses

---

## 8. What is the difference between static and non-static members?

**Answer:**

**Static Members:**
- Belong to class, not instances
- Shared among all instances
- Can be accessed without creating object
- Loaded when class is loaded
- Cannot access non-static members directly

**Non-Static (Instance) Members:**
- Belong to object instances
- Separate copy for each object
- Require object creation to access
- Loaded when object is created
- Can access both static and non-static members

```java
class Counter {
    static int staticCount = 0;      // Shared by all objects
    int instanceCount = 0;           // Separate for each object
    
    static void staticMethod() {
        staticCount++;               // OK
        // instanceCount++;          // ERROR: Cannot access instance member
    }
    
    void instanceMethod() {
        staticCount++;               // OK
        instanceCount++;             // OK
    }
}

// Usage
Counter.staticMethod();              // No object needed
Counter c1 = new Counter();
c1.instanceMethod();                 // Object required
```

**Static Block:**
```java
class Example {
    static {
        // Executed when class is loaded
        System.out.println("Static block");
    }
}
```

---

## 9. What is constructor in Java? Types of constructors?

**Answer:**

A constructor is a special method used to initialize objects. It has the same name as the class and no return type.

**Types of Constructors:**

**1. Default Constructor:**
- No parameters
- Provided by compiler if no constructor defined
- Initializes instance variables to default values

```java
class Student {
    String name;
    int age;
    
    // Default constructor
    Student() {
        name = "Unknown";
        age = 0;
    }
}
```

**2. Parameterized Constructor:**
- Takes parameters to initialize object with specific values

```java
class Student {
    String name;
    int age;
    
    // Parameterized constructor
    Student(String n, int a) {
        name = n;
        age = a;
    }
}
```

**3. Copy Constructor:**
- Initializes object using another object of same class

```java
class Student {
    String name;
    int age;
    
    // Copy constructor
    Student(Student s) {
        name = s.name;
        age = s.age;
    }
}
```

**Constructor Chaining:**
```java
class Student {
    String name;
    int age;
    
    Student() {
        this("Unknown", 0);  // Calls parameterized constructor
    }
    
    Student(String name) {
        this(name, 0);
    }
    
    Student(String name, int age) {
        this.name = name;
        this.age = age;
    }
}
```

**Key Points:**
- Constructor name = Class name
- No return type
- Called automatically when object is created
- Can be overloaded
- Cannot be static, final, or abstract

---

## 10. What is `this` keyword in Java?

**Answer:**

`this` is a reference variable that refers to the current object.

**Uses of `this` keyword:**

**1. Refer to instance variables:**
```java
class Student {
    String name;
    
    Student(String name) {
        this.name = name;  // Distinguish parameter from instance variable
    }
}
```

**2. Invoke current class method:**
```java
class Example {
    void method1() {
        System.out.println("Method 1");
    }
    
    void method2() {
        this.method1();  // Explicit call
        method1();       // Implicit - same as above
    }
}
```

**3. Invoke current class constructor (constructor chaining):**
```java
class Student {
    Student() {
        this("Default");  // Calls parameterized constructor
    }
    
    Student(String name) {
        System.out.println(name);
    }
}
```

**4. Pass as argument:**
```java
class Example {
    void method1(Example obj) {
        System.out.println("Method called");
    }
    
    void method2() {
        method1(this);  // Passing current object
    }
}
```

**5. Return current object:**
```java
class Example {
    Example getInstance() {
        return this;
    }
}
```

**Note:** `this` cannot be used in static context as static members belong to class, not object.

---

## 11. What is inheritance in Java? Types of inheritance?

**Answer:**

Inheritance is a mechanism where one class acquires properties and behaviors of another class.

**Terminology:**
- **Parent Class**: Superclass, Base class
- **Child Class**: Subclass, Derived class
- **Keyword**: `extends`

**Types of Inheritance:**

**1. Single Inheritance:**
```java
class Animal {
    void eat() {
        System.out.println("Eating...");
    }
}

class Dog extends Animal {
    void bark() {
        System.out.println("Barking...");
    }
}
```

**2. Multilevel Inheritance:**
```java
class Animal {
    void eat() {
        System.out.println("Eating...");
    }
}

class Dog extends Animal {
    void bark() {
        System.out.println("Barking...");
    }
}

class Puppy extends Dog {
    void weep() {
        System.out.println("Weeping...");
    }
}
```

**3. Hierarchical Inheritance:**
```java
class Animal {
    void eat() {
        System.out.println("Eating...");
    }
}

class Dog extends Animal {
    void bark() {
        System.out.println("Barking...");
    }
}

class Cat extends Animal {
    void meow() {
        System.out.println("Meowing...");
    }
}
```

**4. Multiple Inheritance (NOT supported in Java with classes):**
- Java doesn't support multiple inheritance with classes to avoid ambiguity (Diamond Problem)
- Achieved through interfaces

```java
interface Flyable {
    void fly();
}

interface Swimmable {
    void swim();
}

class Duck implements Flyable, Swimmable {
    public void fly() {
        System.out.println("Flying...");
    }
    
    public void swim() {
        System.out.println("Swimming...");
    }
}
```

**5. Hybrid Inheritance:**
- Combination of multiple types
- Achieved through interfaces

---

## 12. What is `super` keyword in Java?

**Answer:**

`super` is a reference variable used to refer to the immediate parent class object.

**Uses of `super` keyword:**

**1. Access parent class variables:**
```java
class Parent {
    int num = 10;
}

class Child extends Parent {
    int num = 20;
    
    void display() {
        System.out.println(super.num);  // 10 (parent's num)
        System.out.println(num);        // 20 (child's num)
    }
}
```

**2. Invoke parent class method:**
```java
class Parent {
    void display() {
        System.out.println("Parent display");
    }
}

class Child extends Parent {
    void display() {
        super.display();  // Calls parent's display()
        System.out.println("Child display");
    }
}
```

**3. Invoke parent class constructor:**
```java
class Parent {
    Parent() {
        System.out.println("Parent constructor");
    }
    
    Parent(String name) {
        System.out.println("Parent: " + name);
    }
}

class Child extends Parent {
    Child() {
        super("Java");  // Calls parameterized parent constructor
        System.out.println("Child constructor");
    }
}
```

**Important Points:**
- `super()` must be first statement in constructor
- If not explicitly called, Java automatically inserts `super()` call
- `super` cannot be used in static context
- Used to call overridden methods or hidden variables

---

## 13. What is method overloading?

**Answer:**

Method overloading allows multiple methods with the same name but different parameters in the same class.

**Ways to Overload:**
1. Different number of parameters
2. Different types of parameters
3. Different order of parameters

**NOT considered for overloading:**
- Return type
- Access modifiers
- Exception declarations

**Examples:**

```java
class Calculator {
    // Different number of parameters
    int add(int a, int b) {
        return a + b;
    }
    
    int add(int a, int b, int c) {
        return a + b + c;
    }
    
    // Different types of parameters
    double add(double a, double b) {
        return a + b;
    }
    
    // Different order of parameters
    void display(int a, String b) {
        System.out.println(a + " " + b);
    }
    
    void display(String a, int b) {
        System.out.println(a + " " + b);
    }
}

// Usage
Calculator calc = new Calculator();
calc.add(5, 10);           // Calls add(int, int)
calc.add(5, 10, 15);       // Calls add(int, int, int)
calc.add(5.5, 10.5);       // Calls add(double, double)
```

**Type Promotion in Overloading:**
```java
class Example {
    void method(int a) {
        System.out.println("int: " + a);
    }
    
    void method(long a) {
        System.out.println("long: " + a);
    }
}

Example e = new Example();
e.method(10);    // Calls method(int)
byte b = 10;
e.method(b);     // Calls method(int) - byte promoted to int
```

**Benefits:**
- Increases code readability
- Provides flexibility to call methods with different parameters
- Implements compile-time polymorphism

---

## 14. What is method overriding?

**Answer:**

Method overriding occurs when a subclass provides a specific implementation of a method already defined in its parent class.

**Rules for Method Overriding:**
1. Method name, parameters, and return type must be same
2. Cannot override static methods
3. Cannot override final methods
4. Cannot override private methods
5. Access modifier cannot be more restrictive
6. Can throw same, subclass, or no exception
7. Must be in inheritance relationship

**Example:**

```java
class Animal {
    void makeSound() {
        System.out.println("Animal makes sound");
    }
    
    final void sleep() {
        System.out.println("Animal sleeps");
    }
}

class Dog extends Animal {
    @Override
    void makeSound() {
        System.out.println("Dog barks");
    }
    
    // Cannot override final method
    // void sleep() { }  // Compilation error
}

// Usage
Animal animal = new Dog();
animal.makeSound();  // Output: Dog barks (runtime polymorphism)
```

**Covariant Return Type (Java 5+):**
```java
class Parent {
    Parent getInstance() {
        return new Parent();
    }
}

class Child extends Parent {
    @Override
    Child getInstance() {  // Return type is subclass
        return new Child();
    }
}
```

**Access Modifier Rules:**
```java
class Parent {
    protected void method() { }
}

class Child extends Parent {
    // Valid: Same or less restrictive
    public void method() { }
    
    // Invalid: More restrictive
    // private void method() { }  // Compilation error
}
```

**@Override Annotation:**
- Optional but recommended
- Helps compiler detect errors
- Improves code readability

---

## 15. What is the difference between overloading and overriding?

**Answer:**

| Feature | Method Overloading | Method Overriding |
|---------|-------------------|-------------------|
| **Definition** | Multiple methods with same name, different parameters | Redefining parent class method in child class |
| **Occurrence** | Same class | Different classes (inheritance) |
| **Parameters** | Must be different | Must be same |
| **Return Type** | Can be different | Must be same (or covariant) |
| **Access Modifier** | Can be different | Cannot be more restrictive |
| **Binding** | Compile-time (static) | Runtime (dynamic) |
| **Polymorphism** | Compile-time polymorphism | Runtime polymorphism |
| **Static Methods** | Can be overloaded | Cannot be overridden |
| **Private Methods** | Can be overloaded | Cannot be overridden |
| **Final Methods** | Can be overloaded | Cannot be overridden |
| **Exception** | Independent | Cannot throw broader exceptions |

**Examples:**

```java
// Overloading
class Calculator {
    int add(int a, int b) { return a + b; }
    double add(double a, double b) { return a + b; }  // Overloaded
}

// Overriding
class Parent {
    void display() { System.out.println("Parent"); }
}

class Child extends Parent {
    @Override
    void display() { System.out.println("Child"); }  // Overridden
}
```

---

## 16. What is polymorphism in Java?

**Answer:**

Polymorphism means "many forms". It allows objects to be treated as instances of their parent class while retaining their specific behavior.

**Types of Polymorphism:**

**1. Compile-time Polymorphism (Static Binding):**
- Achieved through method overloading
- Resolved at compile time

```java
class Example {
    void display(int a) {
        System.out.println("Integer: " + a);
    }
    
    void display(String a) {
        System.out.println("String: " + a);
    }
}
```

**2. Runtime Polymorphism (Dynamic Binding):**
- Achieved through method overriding
- Resolved at runtime
- Requires inheritance

```java
class Animal {
    void makeSound() {
        System.out.println("Animal sound");
    }
}

class Dog extends Animal {
    @Override
    void makeSound() {
        System.out.println("Bark");
    }
}

class Cat extends Animal {
    @Override
    void makeSound() {
        System.out.println("Meow");
    }
}

// Usage - Runtime Polymorphism
Animal animal1 = new Dog();
Animal animal2 = new Cat();
animal1.makeSound();  // Output: Bark
animal2.makeSound();  // Output: Meow
```

**Key Concepts:**

**Upcasting (Implicit):**
```java
Dog dog = new Dog();
Animal animal = dog;  // Upcasting
```

**Downcasting (Explicit):**
```java
Animal animal = new Dog();
Dog dog = (Dog) animal;  // Downcasting
```

**instanceof operator:**
```java
if (animal instanceof Dog) {
    Dog dog = (Dog) animal;
    dog.bark();
}
```

**Benefits:**
- Code reusability
- Flexibility
- Maintainability
- Loose coupling

---

## 17. What is encapsulation in Java?

**Answer:**

Encapsulation is the bundling of data (variables) and methods that operate on the data into a single unit (class), and restricting access to some components.

**Key Concepts:**
- Data hiding
- Access control through access modifiers
- Getter and Setter methods

**Implementation:**

```java
class Employee {
    // Private variables - data hiding
    private String name;
    private int age;
    private double salary;
    
    // Public constructor
    public Employee(String name, int age, double salary) {
        this.name = name;
        setAge(age);         // Validation through setter
        setSalary(salary);
    }
    
    // Public getter methods
    public String getName() {
        return name;
    }
    
    public int getAge() {
        return age;
    }
    
    public double getSalary() {
        return salary;
    }
    
    // Public setter methods with validation
    public void setName(String name) {
        if (name != null && !name.isEmpty()) {
            this.name = name;
        }
    }
    
    public void setAge(int age) {
        if (age > 0 && age < 100) {
            this.age = age;
        } else {
            throw new IllegalArgumentException("Invalid age");
        }
    }
    
    public void setSalary(double salary) {
        if (salary > 0) {
            this.salary = salary;
        }
    }
}

// Usage
Employee emp = new Employee("John", 30, 50000);
emp.setAge(35);           // Valid
// emp.age = -5;          // Compilation error - private field
System.out.println(emp.getAge());
```

**Benefits:**
- **Data Security**: Prevents unauthorized access
- **Flexibility**: Can change internal implementation without affecting external code
- **Maintainability**: Easy to modify and maintain
- **Control**: Validation and control over data
- **Loose Coupling**: Reduces dependencies

**Real-world Example:**
```java
class BankAccount {
    private double balance;
    
    public void deposit(double amount) {
        if (amount > 0) {
            balance += amount;
        }
    }
    
    public boolean withdraw(double amount) {
        if (amount > 0 && balance >= amount) {
            balance -= amount;
            return true;
        }
        return false;
    }
    
    public double getBalance() {
        return balance;
    }
}
```

---

## 18. What is abstraction in Java?

**Answer:**

Abstraction is hiding implementation details and showing only essential features to the user.

**Ways to Achieve Abstraction:**

**1. Abstract Class (0-100% abstraction):**
```java
abstract class Vehicle {
    // Abstract method - no implementation
    abstract void start();
    abstract void stop();
    
    // Concrete method - with implementation
    void fuel() {
        System.out.println("Refueling...");
    }
}

class Car extends Vehicle {
    @Override
    void start() {
        System.out.println("Car starting with key");
    }
    
    @Override
    void stop() {
        System.out.println("Car stopping with brake");
    }
}

// Usage
Vehicle vehicle = new Car();
vehicle.start();
vehicle.fuel();
```

**2. Interface (100% abstraction - before Java 8):**
```java
interface Drawable {
    void draw();  // public abstract by default
}

class Circle implements Drawable {
    @Override
    public void draw() {
        System.out.println("Drawing circle");
    }
}
```

**Abstract Class Rules:**
- Cannot be instantiated
- Can have abstract and concrete methods
- Can have constructors
- Can have instance variables
- Can have static methods
- Can have final methods
- Use `abstract` keyword

**Example with Constructor:**
```java
abstract class Animal {
    String name;
    
    // Constructor in abstract class
    Animal(String name) {
        this.name = name;
    }
    
    abstract void makeSound();
    
    void sleep() {
        System.out.println(name + " is sleeping");
    }
}

class Dog extends Animal {
    Dog(String name) {
        super(name);
    }
    
    @Override
    void makeSound() {
        System.out.println("Woof!");
    }
}
```

**Benefits:**
- Reduces complexity
- Provides security
- Increases code reusability
- Provides loose coupling
- Separates what from how

**Abstraction vs Encapsulation:**
- **Abstraction**: Hides complexity (what to show)
- **Encapsulation**: Hides data (how to hide)

---

## 19. What is an interface in Java?

**Answer:**

An interface is a blueprint of a class that contains only abstract methods (before Java 8) and static final variables.

**Key Features:**
- All methods are `public abstract` by default
- All variables are `public static final` by default
- Cannot have constructors
- Cannot be instantiated
- A class can implement multiple interfaces
- Provides 100% abstraction (before Java 8)

**Basic Interface:**
```java
interface Animal {
    // public static final by default
    int LEGS = 4;
    
    // public abstract by default
    void eat();
    void sleep();
}

class Dog implements Animal {
    @Override
    public void eat() {
        System.out.println("Dog eating");
    }
    
    @Override
    public void sleep() {
        System.out.println("Dog sleeping");
    }
}
```

**Multiple Interface Implementation:**
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
```

**Interface Inheritance:**
```java
interface Animal {
    void eat();
}

interface Mammal extends Animal {
    void breathe();
}

class Human implements Mammal {
    @Override
    public void eat() {
        System.out.println("Human eating");
    }
    
    @Override
    public void breathe() {
        System.out.println("Human breathing");
    }
}
```

**Java 8+ Features:**
```java
interface MyInterface {
    // Abstract method
    void abstractMethod();
    
    // Default method (Java 8+)
    default void defaultMethod() {
        System.out.println("Default implementation");
    }
    
    // Static method (Java 8+)
    static void staticMethod() {
        System.out.println("Static method in interface");
    }
}

// Java 9+: Private methods
interface AdvancedInterface {
    default void method1() {
        commonLogic();
    }
    
    default void method2() {
        commonLogic();
    }
    
    private void commonLogic() {
        System.out.println("Common logic");
    }
}
```

**Marker/Tagging Interface:**
```java
// Empty interface - used to mark classes
interface Serializable {
}

class Student implements Serializable {
    // Now Student objects can be serialized
}
```

**Functional Interface (Java 8+):**
```java
@FunctionalInterface
interface Calculator {
    int calculate(int a, int b);  // Only one abstract method
}

// Lambda expression
Calculator add = (a, b) -> a + b;
System.out.println(add.calculate(5, 3));  // 8
```

---

## 20. What is the difference between abstract class and interface?

**Answer:**

| Feature | Abstract Class | Interface |
|---------|----------------|-----------|
| **Keyword** | `abstract` | `interface` |
| **Methods** | Abstract and concrete methods | All abstract (before Java 8) |
| **Variables** | Any type of variables | Only `public static final` |
| **Constructor** | Can have constructors | Cannot have constructors |
| **Access Modifiers** | Any access modifier | Only `public` (or default in Java 9+) |
| **Multiple Inheritance** | Not supported | Supported |
| **Extends/Implements** | Class `extends` one abstract class | Class `implements` multiple interfaces |
| **When to Use** | Common base with shared code | Contract for unrelated classes |
| **Abstraction** | 0-100% | 100% (before Java 8) |
| **Performance** | Slightly faster | Slightly slower |
| **Default Methods** | Not needed | Java 8+ feature |
| **Static Methods** | Allowed | Java 8+ allowed |
| **Instantiation** | Cannot be instantiated | Cannot be instantiated |

**When to Use Abstract Class:**
- Code reusability through inheritance
- Common functionality for related classes
- Need non-static, non-final fields
- Need access modifiers other than public

**When to Use Interface:**
- Multiple inheritance needed
- Define contract for unrelated classes
- Achieve loose coupling
- API definition

**Example:**
```java
// Abstract class for related classes
abstract class Animal {
    String name;  // Instance variable
    
    Animal(String name) {
        this.name = name;
    }
    
    abstract void makeSound();
    
    void sleep() {  // Common implementation
        System.out.println(name + " sleeping");
    }
}

// Interface for unrelated classes
interface Flyable {
    void fly();
}

class Bird extends Animal implements Flyable {
    Bird(String name) {
        super(name);
    }
    
    @Override
    void makeSound() {
        System.out.println("Chirp");
    }
    
    @Override
    public void fly() {
        System.out.println(name + " flying");
    }
}

class Airplane implements Flyable {
    @Override
    public void fly() {
        System.out.println("Airplane flying");
    }
}
```
