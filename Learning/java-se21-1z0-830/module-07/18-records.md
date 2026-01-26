# Records in Java

## Introduction

Records are a special kind of class introduced in Java 14 (preview) and finalized in Java 16. Records provide a compact syntax for declaring classes that are transparent holders for immutable data. They eliminate boilerplate code associated with data carrier classes.

## What are Records?

A record is a special class designed to hold immutable data. When you declare a record, Java automatically generates:
- Private final fields
- Public constructor
- Public accessor methods
- `equals()`, `hashCode()`, and `toString()` methods

### Basic Record Syntax

```java
// Traditional class - verbose
class Point {
    private final int x;
    private final int y;
    
    public Point(int x, int y) {
        this.x = x;
        this.y = y;
    }
    
    public int x() { return x; }
    public int y() { return y; }
    
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof Point)) return false;
        Point point = (Point) o;
        return x == point.x && y == point.y;
    }
    
    @Override
    public int hashCode() {
        return Objects.hash(x, y);
    }
    
    @Override
    public String toString() {
        return "Point[x=" + x + ", y=" + y + "]";
    }
}

// Record - concise!
record Point(int x, int y) { }

// Usage
public class RecordDemo {
    public static void main(String[] args) {
        Point p = new Point(10, 20);
        System.out.println(p.x());           // 10
        System.out.println(p.y());           // 20
        System.out.println(p);               // Point[x=10, y=20]
    }
}
```

## Record Components

The parameters in the record header are called **components**. They define:
- Private final fields
- Public accessor methods (not getters!)
- Constructor parameters

```java
record Person(String name, int age) { }

public class ComponentsDemo {
    public static void main(String[] args) {
        Person person = new Person("Alice", 30);
        
        // Accessor methods named after components (not getX/getY)
        String name = person.name();  // Not getName()!
        int age = person.age();       // Not getAge()!
        
        System.out.println(name + " is " + age + " years old");
    }
}
```

## Automatically Generated Methods

### Canonical Constructor

Java generates a canonical constructor that initializes all fields:

```java
record Book(String title, String author, int year) { }

// Java generates:
// public Book(String title, String author, int year) {
//     this.title = title;
//     this.author = author;
//     this.year = year;
// }

public class CanonicalConstructorDemo {
    public static void main(String[] args) {
        Book book = new Book("1984", "George Orwell", 1949);
        System.out.println(book);
        // Output: Book[title=1984, author=George Orwell, year=1949]
    }
}
```

### equals() Method

Records automatically implement `equals()` based on all components:

```java
record Color(int red, int green, int blue) { }

public class EqualsDemo {
    public static void main(String[] args) {
        Color c1 = new Color(255, 0, 0);
        Color c2 = new Color(255, 0, 0);
        Color c3 = new Color(0, 255, 0);
        
        System.out.println(c1.equals(c2));  // true
        System.out.println(c1.equals(c3));  // false
    }
}
```

### hashCode() Method

Records automatically implement `hashCode()` based on all components:

```java
record Employee(int id, String name) { }

public class HashCodeDemo {
    public static void main(String[] args) {
        Employee e1 = new Employee(1, "Alice");
        Employee e2 = new Employee(1, "Alice");
        
        System.out.println(e1.hashCode() == e2.hashCode());  // true
        
        // Can be used in HashSet/HashMap
        Set<Employee> employees = new HashSet<>();
        employees.add(e1);
        System.out.println(employees.contains(e2));  // true
    }
}
```

### toString() Method

Records automatically implement a readable `toString()`:

```java
record Rectangle(double length, double width) { }

public class ToStringDemo {
    public static void main(String[] args) {
        Rectangle rect = new Rectangle(10.5, 5.0);
        System.out.println(rect);
        // Output: Rectangle[length=10.5, width=5.0]
    }
}
```

## Custom Constructors

### Compact Constructor

A compact constructor allows validation without repeating parameters:

```java
record Range(int min, int max) {
    // Compact constructor - no parameter list
    public Range {
        if (min > max) {
            throw new IllegalArgumentException("min must be <= max");
        }
        // Fields are assigned automatically after this block
    }
}

public class CompactConstructorDemo {
    public static void main(String[] args) {
        Range valid = new Range(1, 10);      // OK
        // Range invalid = new Range(10, 1); // IllegalArgumentException
    }
}
```

### Canonical Constructor Override

You can override the canonical constructor with full parameter list:

```java
record Person(String name, int age) {
    // Full canonical constructor
    public Person(String name, int age) {
        if (age < 0) {
            throw new IllegalArgumentException("Age cannot be negative");
        }
        this.name = name.toUpperCase();  // Normalize
        this.age = age;
    }
}
```

### Additional Constructors

Records can have additional constructors, but they must delegate to the canonical constructor:

```java
record Point(int x, int y) {
    // Compact constructor for validation
    public Point {
        if (x < 0 || y < 0) {
            throw new IllegalArgumentException("Coordinates must be non-negative");
        }
    }
    
    // Additional constructor - must call canonical constructor
    public Point() {
        this(0, 0);  // Delegate to canonical constructor
    }
}

public class AdditionalConstructorDemo {
    public static void main(String[] args) {
        Point p1 = new Point(5, 10);  // Canonical constructor
        Point p2 = new Point();       // Additional constructor
        System.out.println(p2);       // Point[x=0, y=0]
    }
}
```

## Instance Methods in Records

Records can have instance methods:

```java
record Circle(double radius) {
    // Instance methods
    public double area() {
        return Math.PI * radius * radius;
    }
    
    public double circumference() {
        return 2 * Math.PI * radius;
    }
    
    public Circle scale(double factor) {
        return new Circle(radius * factor);
    }
}

public class MethodsDemo {
    public static void main(String[] args) {
        Circle circle = new Circle(5.0);
        System.out.println("Area: " + circle.area());
        System.out.println("Circumference: " + circle.circumference());
        
        Circle scaled = circle.scale(2.0);
        System.out.println("Scaled radius: " + scaled.radius());
    }
}
```

## Static Members in Records

Records can have static fields and methods:

```java
record MathConstants(String name, double value) {
    // Static fields
    public static final MathConstants PI = new MathConstants("Pi", Math.PI);
    public static final MathConstants E = new MathConstants("Euler's number", Math.E);
    
    // Static methods
    public static MathConstants create(String name, double value) {
        return new MathConstants(name, value);
    }
    
    // Static initializer
    static {
        System.out.println("MathConstants class loaded");
    }
}

public class StaticMembersDemo {
    public static void main(String[] args) {
        System.out.println(MathConstants.PI);
        System.out.println(MathConstants.E);
    }
}
```

## Records Implementing Interfaces

Records can implement interfaces:

```java
interface Drawable {
    void draw();
}

record Circle(double radius) implements Drawable {
    @Override
    public void draw() {
        System.out.println("Drawing circle with radius: " + radius);
    }
}

record Rectangle(double length, double width) implements Drawable {
    @Override
    public void draw() {
        System.out.println("Drawing rectangle: " + length + "x" + width);
    }
}

public class InterfaceDemo {
    public static void main(String[] args) {
        List<Drawable> shapes = List.of(
            new Circle(5.0),
            new Rectangle(10.0, 5.0)
        );
        
        shapes.forEach(Drawable::draw);
    }
}
```

## Nested Records

Records can be nested within classes or other records:

```java
public class Organization {
    record Employee(int id, String name, Address address) { }
    
    record Address(String street, String city, String zip) { }
}

public class NestedRecordDemo {
    public static void main(String[] args) {
        Organization.Address address = new Organization.Address(
            "123 Main St", "Springfield", "12345"
        );
        
        Organization.Employee emp = new Organization.Employee(
            1, "Alice", address
        );
        
        System.out.println(emp);
    }
}
```

## Generic Records

Records can be generic:

```java
record Pair<T, U>(T first, U second) { }

public class GenericRecordDemo {
    public static void main(String[] args) {
        Pair<String, Integer> pair1 = new Pair<>("Age", 30);
        Pair<Double, Double> pair2 = new Pair<>(10.5, 20.3);
        
        System.out.println(pair1);  // Pair[first=Age, second=30]
        System.out.println(pair2);  // Pair[first=10.5, second=20.3]
    }
}
```

## Record Restrictions

### Cannot Extend Classes

Records implicitly extend `java.lang.Record` and cannot extend other classes:

```java
class Parent { }

// ERROR: Cannot extend class
// record Child(int value) extends Parent { }  // Compilation error!
```

### Fields Must Be Final

Record components create final fields that cannot be modified:

```java
record Person(String name, int age) {
    // ERROR: Cannot add non-final instance fields
    // private int salary;  // Compilation error!
    
    // OK: Static fields allowed
    private static int count = 0;
}

public class ImmutabilityDemo {
    public static void main(String[] args) {
        Person person = new Person("Alice", 30);
        // person.name = "Bob";  // ERROR: Cannot access private final field
    }
}
```

### Cannot Be Abstract

Records cannot be declared abstract:

```java
// ERROR: Records cannot be abstract
// abstract record Shape(String name) { }  // Compilation error!
```

### Accessor Methods Cannot Be Overridden with Different Return Type

```java
record Point(int x, int y) {
    // ERROR: Cannot change return type
    // public double x() { return x; }  // Compilation error!
    
    // OK: Can override with same return type
    public int x() {
        System.out.println("Getting x");
        return x;
    }
}
```

## Pattern Matching with Records (Java 21)

Records work seamlessly with pattern matching:

```java
record Point(int x, int y) { }

public class PatternMatchingDemo {
    public static void process(Object obj) {
        // Pattern matching for instanceof with record deconstruction
        if (obj instanceof Point(int x, int y)) {
            System.out.println("Point at (" + x + ", " + y + ")");
        }
    }
    
    public static String describe(Object obj) {
        return switch (obj) {
            case Point(int x, int y) -> "Point at (" + x + ", " + y + ")";
            case null -> "null";
            default -> "Unknown";
        };
    }
    
    public static void main(String[] args) {
        Point p = new Point(10, 20);
        process(p);  // Point at (10, 20)
        System.out.println(describe(p));
    }
}
```

### Nested Pattern Matching

```java
record Point(int x, int y) { }
record Rectangle(Point topLeft, Point bottomRight) { }

public class NestedPatternDemo {
    public static void processRectangle(Object obj) {
        if (obj instanceof Rectangle(Point(int x1, int y1), Point(int x2, int y2))) {
            int width = x2 - x1;
            int height = y2 - y1;
            System.out.println("Rectangle: " + width + "x" + height);
        }
    }
    
    public static void main(String[] args) {
        Rectangle rect = new Rectangle(
            new Point(0, 0),
            new Point(10, 20)
        );
        processRectangle(rect);  // Rectangle: 10x20
    }
}
```

## Use Cases for Records

### 1. Data Transfer Objects (DTOs)

```java
record UserDTO(long id, String username, String email) { }

record OrderDTO(long orderId, List<ItemDTO> items, double total) { }

record ItemDTO(String productId, int quantity, double price) { }
```

### 2. Returning Multiple Values

```java
record Result(boolean success, String message, Object data) { }

public class Service {
    public Result processData(String input) {
        if (input == null) {
            return new Result(false, "Input cannot be null", null);
        }
        // Process...
        return new Result(true, "Success", processedData);
    }
}
```

### 3. Immutable Configuration

```java
record DatabaseConfig(
    String url,
    String username,
    String password,
    int maxConnections
) {
    public DatabaseConfig {
        if (maxConnections <= 0) {
            throw new IllegalArgumentException("Max connections must be positive");
        }
    }
}
```

### 4. Value Objects

```java
record Money(double amount, String currency) {
    public Money add(Money other) {
        if (!currency.equals(other.currency)) {
            throw new IllegalArgumentException("Currency mismatch");
        }
        return new Money(amount + other.amount, currency);
    }
}

public class ValueObjectDemo {
    public static void main(String[] args) {
        Money m1 = new Money(100, "USD");
        Money m2 = new Money(50, "USD");
        Money total = m1.add(m2);
        System.out.println(total);  // Money[amount=150.0, currency=USD]
    }
}
```

## Records vs Classes

| Feature | Record | Regular Class |
|---------|--------|---------------|
| Boilerplate | Minimal | Manual |
| Mutability | Immutable | Mutable by default |
| Inheritance | Cannot extend classes | Can extend classes |
| Fields | Implicitly final | Any modifier |
| Constructor | Auto-generated | Manual |
| equals/hashCode | Auto-generated | Manual |
| toString | Auto-generated | Manual |
| Use case | Data carriers | Any purpose |

## Best Practices

### 1. Use Records for Simple Data Carriers

```java
// Good - simple data holder
record Coordinate(double latitude, double longitude) { }

// Bad - complex business logic better in class
// record UserService(Database db) { ... complex logic ... }
```

### 2. Validate in Compact Constructor

```java
record Email(String address) {
    public Email {
        if (!address.contains("@")) {
            throw new IllegalArgumentException("Invalid email");
        }
    }
}
```

### 3. Be Careful with Mutable Components

```java
// Potential issue - List is mutable
record Order(List<String> items) { }

public class MutableComponentDemo {
    public static void main(String[] args) {
        List<String> items = new ArrayList<>();
        items.add("Item1");
        
        Order order = new Order(items);
        items.add("Item2");  // Modifies the record's data!
        
        System.out.println(order);  // Order[items=[Item1, Item2]]
    }
}

// Better - defensive copy
record SafeOrder(List<String> items) {
    public SafeOrder(List<String> items) {
        this.items = List.copyOf(items);  // Immutable copy
    }
}
```

## Summary

- **Records** provide compact syntax for immutable data carriers
- Automatically generate **constructor, accessors, equals(), hashCode(), toString()**
- Record components create **private final fields**
- Accessor methods named after components (not `getX()`)
- **Compact constructor** enables validation without parameter repetition
- Records can have **instance methods, static members, and implement interfaces**
- Records **cannot extend classes** (implicitly extend Record)
- Records are **implicitly final** and cannot be abstract
- Work with **pattern matching** for deconstruction (Java 21)
- Use for **DTOs, value objects, and returning multiple values**
- Be careful with **mutable components** - use defensive copying
