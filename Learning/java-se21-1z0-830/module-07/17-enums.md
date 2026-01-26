# Enumerations (Enums) in Java

## Introduction

Enumerations (enums) are a special data type in Java that represents a fixed set of constants. Introduced in Java 5, enums provide a type-safe way to work with a predefined set of values, making code more readable and maintainable.

## What are Enums?

An enum is a reference type that defines a collection of constants. Each constant is an instance of the enum type.

### Basic Enum Declaration

```java
enum Day {
    MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY
}

public class EnumDemo {
    public static void main(String[] args) {
        Day today = Day.MONDAY;
        System.out.println("Today is: " + today);
        
        // Comparison
        if (today == Day.MONDAY) {
            System.out.println("Start of the work week");
        }
    }
}
```

### Enum Characteristics

1. **Type-safe**: Cannot assign arbitrary values
2. **Fixed set**: Constants are defined at compile time
3. **Singleton**: Each enum constant is a singleton instance
4. **Comparable**: Enums implement Comparable by declaration order
5. **Serializable**: Enums are automatically serializable

```java
enum Color {
    RED, GREEN, BLUE
}

public class TypeSafetyDemo {
    public static void main(String[] args) {
        Color color = Color.RED;
        
        // Type-safe - cannot assign arbitrary values
        // color = "RED";  // Compilation error!
        // color = 1;      // Compilation error!
        
        // Only valid enum constants allowed
        color = Color.BLUE;  // OK
    }
}
```

## Enum Methods

Every enum automatically inherits from `java.lang.Enum` and has several built-in methods:

### values() Method

Returns an array of all enum constants:

```java
enum Season {
    SPRING, SUMMER, FALL, WINTER
}

public class ValuesDemo {
    public static void main(String[] args) {
        // Get all enum values
        Season[] seasons = Season.values();
        
        for (Season season : seasons) {
            System.out.println(season);
        }
        // Output:
        // SPRING
        // SUMMER
        // FALL
        // WINTER
    }
}
```

### valueOf() Method

Converts a string to an enum constant:

```java
enum Status {
    PENDING, APPROVED, REJECTED
}

public class ValueOfDemo {
    public static void main(String[] args) {
        // Convert string to enum
        Status status = Status.valueOf("APPROVED");
        System.out.println(status);  // APPROVED
        
        // Case-sensitive - throws IllegalArgumentException if not found
        try {
            Status invalid = Status.valueOf("approved");  // Wrong case!
        } catch (IllegalArgumentException e) {
            System.out.println("Invalid enum constant");
        }
    }
}
```

### name() Method

Returns the name of the enum constant as a string:

```java
enum Priority {
    LOW, MEDIUM, HIGH
}

public class NameDemo {
    public static void main(String[] args) {
        Priority p = Priority.HIGH;
        String name = p.name();  // "HIGH"
        System.out.println(name);
    }
}
```

### ordinal() Method

Returns the position of the enum constant (zero-based):

```java
enum Month {
    JAN, FEB, MAR, APR, MAY, JUN, JUL, AUG, SEP, OCT, NOV, DEC
}

public class OrdinalDemo {
    public static void main(String[] args) {
        Month month = Month.JAN;
        System.out.println(month.ordinal());  // 0
        
        month = Month.DEC;
        System.out.println(month.ordinal());  // 11
    }
}
```

## Enums with Fields, Constructors, and Methods

Enums can have fields, constructors, and methods like regular classes:

```java
enum Planet {
    MERCURY(3.303e+23, 2.4397e6),
    VENUS(4.869e+24, 6.0518e6),
    EARTH(5.976e+24, 6.37814e6),
    MARS(6.421e+23, 3.3972e6);
    
    private final double mass;   // in kilograms
    private final double radius; // in meters
    
    // Constructor - must be private or package-private
    Planet(double mass, double radius) {
        this.mass = mass;
        this.radius = radius;
    }
    
    // Instance methods
    public double getMass() {
        return mass;
    }
    
    public double getRadius() {
        return radius;
    }
    
    public double surfaceGravity() {
        final double G = 6.67300E-11;
        return G * mass / (radius * radius);
    }
}

public class PlanetDemo {
    public static void main(String[] args) {
        Planet earth = Planet.EARTH;
        System.out.printf("Earth mass: %e kg%n", earth.getMass());
        System.out.printf("Earth radius: %e m%n", earth.getRadius());
        System.out.printf("Earth surface gravity: %.2f m/s²%n", 
            earth.surfaceGravity());
    }
}
```

### Enum Constructor Rules

```java
enum Size {
    // Enum constants call constructor
    SMALL("S"),
    MEDIUM("M"),
    LARGE("L");
    
    private final String abbreviation;
    
    // Constructor is implicitly private
    Size(String abbreviation) {
        this.abbreviation = abbreviation;
    }
    
    // ILLEGAL: Constructor cannot be public or protected
    // public Size(String abbreviation) { }  // Compilation error!
    
    public String getAbbreviation() {
        return abbreviation;
    }
}
```

## Enums with Abstract Methods

Enums can have abstract methods that each constant must implement:

```java
enum Operation {
    PLUS {
        @Override
        public double apply(double x, double y) {
            return x + y;
        }
    },
    MINUS {
        @Override
        public double apply(double x, double y) {
            return x - y;
        }
    },
    MULTIPLY {
        @Override
        public double apply(double x, double y) {
            return x * y;
        }
    },
    DIVIDE {
        @Override
        public double apply(double x, double y) {
            return x / y;
        }
    };
    
    // Abstract method - each constant must implement
    public abstract double apply(double x, double y);
}

public class OperationDemo {
    public static void main(String[] args) {
        double x = 10, y = 5;
        
        for (Operation op : Operation.values()) {
            System.out.printf("%f %s %f = %f%n", 
                x, op, y, op.apply(x, y));
        }
        // Output:
        // 10.000000 PLUS 5.000000 = 15.000000
        // 10.000000 MINUS 5.000000 = 5.000000
        // 10.000000 MULTIPLY 5.000000 = 50.000000
        // 10.000000 DIVIDE 5.000000 = 2.000000
    }
}
```

## Enums in Switch Statements

Enums work seamlessly with switch statements:

```java
enum TrafficLight {
    RED, YELLOW, GREEN
}

public class SwitchDemo {
    public static void processLight(TrafficLight light) {
        switch (light) {
            case RED:
                System.out.println("Stop!");
                break;
            case YELLOW:
                System.out.println("Caution!");
                break;
            case GREEN:
                System.out.println("Go!");
                break;
        }
    }
    
    public static void main(String[] args) {
        processLight(TrafficLight.RED);     // Stop!
        processLight(TrafficLight.YELLOW);  // Caution!
        processLight(TrafficLight.GREEN);   // Go!
    }
}
```

### Switch Expressions with Enums (Java 14+)

```java
enum Status {
    PENDING, APPROVED, REJECTED
}

public class SwitchExpressionDemo {
    public static String getMessage(Status status) {
        return switch (status) {
            case PENDING -> "Awaiting review";
            case APPROVED -> "Request approved";
            case REJECTED -> "Request rejected";
        };
    }
    
    public static void main(String[] args) {
        System.out.println(getMessage(Status.PENDING));   // Awaiting review
        System.out.println(getMessage(Status.APPROVED));  // Request approved
    }
}
```

## Enum Comparison

Enums can be compared using `==` or `equals()`:

```java
enum Level {
    LOW, MEDIUM, HIGH
}

public class ComparisonDemo {
    public static void main(String[] args) {
        Level level1 = Level.HIGH;
        Level level2 = Level.HIGH;
        Level level3 = Level.valueOf("HIGH");
        
        // Using == (preferred for enums)
        System.out.println(level1 == level2);      // true
        System.out.println(level1 == level3);      // true
        
        // Using equals()
        System.out.println(level1.equals(level2)); // true
        
        // Null-safe with ==
        Level level4 = null;
        // System.out.println(level4.equals(level1)); // NullPointerException!
        System.out.println(level4 == level1);        // false (no exception)
    }
}
```

## EnumSet and EnumMap

Java provides specialized collections for enums:

### EnumSet

Efficient set implementation for enums:

```java
import java.util.EnumSet;

enum Day {
    MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY
}

public class EnumSetDemo {
    public static void main(String[] args) {
        // Create EnumSet with all values
        EnumSet<Day> allDays = EnumSet.allOf(Day.class);
        System.out.println("All days: " + allDays);
        
        // Create EnumSet with specific values
        EnumSet<Day> weekend = EnumSet.of(Day.SATURDAY, Day.SUNDAY);
        System.out.println("Weekend: " + weekend);
        
        // Create EnumSet with range
        EnumSet<Day> weekdays = EnumSet.range(Day.MONDAY, Day.FRIDAY);
        System.out.println("Weekdays: " + weekdays);
        
        // Complement
        EnumSet<Day> notWeekend = EnumSet.complementOf(weekend);
        System.out.println("Not weekend: " + notWeekend);
    }
}
```

### EnumMap

Efficient map implementation with enum keys:

```java
import java.util.EnumMap;

enum Size {
    SMALL, MEDIUM, LARGE
}

public class EnumMapDemo {
    public static void main(String[] args) {
        EnumMap<Size, Integer> stock = new EnumMap<>(Size.class);
        
        stock.put(Size.SMALL, 10);
        stock.put(Size.MEDIUM, 25);
        stock.put(Size.LARGE, 15);
        
        System.out.println("Stock levels:");
        for (Size size : stock.keySet()) {
            System.out.println(size + ": " + stock.get(size));
        }
    }
}
```

## Enum Implementing Interfaces

Enums can implement interfaces:

```java
interface Describable {
    String getDescription();
}

enum Animal implements Describable {
    DOG("Man's best friend"),
    CAT("Independent feline"),
    BIRD("Can fly");
    
    private final String description;
    
    Animal(String description) {
        this.description = description;
    }
    
    @Override
    public String getDescription() {
        return description;
    }
}

public class InterfaceDemo {
    public static void main(String[] args) {
        for (Animal animal : Animal.values()) {
            System.out.println(animal + ": " + animal.getDescription());
        }
    }
}
```

## Nested Enums

Enums can be nested within classes or other enums:

```java
public class Pizza {
    public enum Size {
        SMALL(10), MEDIUM(12), LARGE(14);
        
        private final int diameter;
        
        Size(int diameter) {
            this.diameter = diameter;
        }
        
        public int getDiameter() {
            return diameter;
        }
    }
    
    public enum Topping {
        CHEESE, PEPPERONI, MUSHROOM, ONION
    }
    
    private Size size;
    private Set<Topping> toppings;
    
    public Pizza(Size size, Topping... toppings) {
        this.size = size;
        this.toppings = new HashSet<>(Arrays.asList(toppings));
    }
}

public class NestedEnumDemo {
    public static void main(String[] args) {
        Pizza pizza = new Pizza(
            Pizza.Size.LARGE,
            Pizza.Topping.CHEESE,
            Pizza.Topping.PEPPERONI
        );
    }
}
```

## Common Enum Patterns

### Singleton Pattern

```java
enum DatabaseConnection {
    INSTANCE;
    
    private Connection connection;
    
    DatabaseConnection() {
        // Initialize connection
        System.out.println("Creating database connection");
    }
    
    public Connection getConnection() {
        return connection;
    }
}

// Usage
DatabaseConnection.INSTANCE.getConnection();
```

### Strategy Pattern

```java
enum PaymentType {
    CASH {
        @Override
        public void pay(double amount) {
            System.out.println("Paid " + amount + " in cash");
        }
    },
    CREDIT_CARD {
        @Override
        public void pay(double amount) {
            System.out.println("Charged " + amount + " to credit card");
        }
    },
    PAYPAL {
        @Override
        public void pay(double amount) {
            System.out.println("Transferred " + amount + " via PayPal");
        }
    };
    
    public abstract void pay(double amount);
}
```

## Best Practices

### 1. Use Enums Instead of Constants

```java
// Bad - error-prone
public class Status {
    public static final int PENDING = 0;
    public static final int APPROVED = 1;
    public static final int REJECTED = 2;
}

// Good - type-safe
enum Status {
    PENDING, APPROVED, REJECTED
}
```

### 2. Override toString() for Custom Display

```java
enum Size {
    SMALL("Small (S)"),
    MEDIUM("Medium (M)"),
    LARGE("Large (L)");
    
    private final String displayName;
    
    Size(String displayName) {
        this.displayName = displayName;
    }
    
    @Override
    public String toString() {
        return displayName;
    }
}
```

### 3. Avoid Using ordinal() for Business Logic

```java
// Bad - fragile if enum order changes
enum Priority {
    LOW, MEDIUM, HIGH
}

int level = Priority.HIGH.ordinal();  // Don't rely on this!

// Good - explicit values
enum Priority {
    LOW(1), MEDIUM(2), HIGH(3);
    
    private final int level;
    
    Priority(int level) {
        this.level = level;
    }
    
    public int getLevel() {
        return level;
    }
}
```

## Summary

- **Enums** represent a fixed set of constants in a type-safe manner
- Enum constants are **singleton instances** of the enum type
- Enums can have **fields, constructors, and methods**
- Enum constructors are **implicitly private**
- Built-in methods: **values()**, **valueOf()**, **name()**, **ordinal()**
- Enums work with **switch statements** and switch expressions
- Enums can have **abstract methods** implemented by each constant
- **EnumSet** and **EnumMap** provide efficient enum-specific collections
- Enums can **implement interfaces** but cannot extend classes
- Use **==** for enum comparison (preferred over equals())
- Enums are automatically **Comparable** and **Serializable**
