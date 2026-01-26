# Pattern Matching and Sealed Classes

## Introduction

Java has evolved to include powerful features that make code more expressive and type-safe. Pattern matching (introduced in stages from Java 14-21) and sealed classes (Java 17) represent modern approaches to handling types and control flow. These features reduce boilerplate code while increasing safety and clarity.

## Pattern Matching for instanceof (Java 16+)

### Traditional instanceof with Casting

Before Java 16, checking and casting required verbose code:

```java
// Before Java 16 - verbose and repetitive
public void processObject(Object obj) {
    if (obj instanceof String) {
        String str = (String) obj;  // Explicit cast
        System.out.println("String length: " + str.length());
    }
}
```

### Pattern Matching Syntax

Java 16 introduced pattern matching for `instanceof`, combining type checking and casting:

```java
// Java 16+ - concise pattern matching
public void processObject(Object obj) {
    if (obj instanceof String str) {  // Test and bind in one expression
        System.out.println("String length: " + str.length());
        // 'str' is automatically cast and in scope
    }
}
```

### Scope of Pattern Variables

Pattern variables have specific scope rules based on definite assignment:

```java
public class ScopeDemo {
    public static void checkType(Object obj) {
        // Simple if statement
        if (obj instanceof String str) {
            System.out.println(str.length());  // 'str' in scope
        }
        // str NOT in scope here
        
        // With else clause
        if (obj instanceof String str) {
            System.out.println(str.toUpperCase());  // str in scope
        } else {
            // str NOT in scope (instanceof was false)
        }
        
        // Negated instanceof
        if (!(obj instanceof String str)) {
            // str NOT in scope (condition is negated)
        } else {
            System.out.println(str.length());  // str in scope here
        }
        
        // With logical AND
        if (obj instanceof String str && str.length() > 5) {
            System.out.println("Long string: " + str);  // str in scope
        }
        
        // ILLEGAL: With logical OR
        // if (obj instanceof String str || str.length() > 0) {
        //     // Compilation error! str might not be assigned
        // }
        
        // In return statement
        int length = obj instanceof String str ? str.length() : 0;
    }
}
```

### Flow Scoping Examples

```java
public class FlowScopingDemo {
    // Pattern variable in method chain
    public static void processString(Object obj) {
        if (obj instanceof String str && !str.isEmpty()) {
            System.out.println("Non-empty string: " + str);
        }
    }
    
    // Multiple pattern variables
    public static void compareObjects(Object obj1, Object obj2) {
        if (obj1 instanceof String s1 && obj2 instanceof String s2) {
            System.out.println("Both are strings");
            System.out.println("s1 length: " + s1.length());
            System.out.println("s2 length: " + s2.length());
        }
    }
    
    // Pattern variable shadowing
    public static void shadowingExample() {
        Object obj = "Hello";
        
        if (obj instanceof String str) {
            System.out.println(str);  // Pattern variable 'str'
            
            String str = "World";  // ERROR: Can't redeclare in same scope
        }
    }
}
```

## Pattern Matching for switch (Java 21)

### Traditional switch Limitations

Before pattern matching, switch statements only worked with primitive types, enums, and strings:

```java
// Traditional switch - limited to specific types
public String describe(Object obj) {
    String result;
    if (obj instanceof Integer) {
        result = "Integer: " + obj;
    } else if (obj instanceof String) {
        result = "String: " + obj;
    } else if (obj instanceof Double) {
        result = "Double: " + obj;
    } else {
        result = "Unknown type";
    }
    return result;
}
```

### Pattern Matching switch Expression

Java 21 allows pattern matching in switch expressions and statements:

```java
// Java 21 - Pattern matching switch
public String describe(Object obj) {
    return switch (obj) {
        case Integer i -> "Integer: " + i;
        case String s  -> "String: " + s;
        case Double d  -> "Double: " + d;
        case null      -> "It's null";
        default        -> "Unknown type";
    };
}
```

### Guard Patterns (when clause)

Use guards to add conditions to patterns:

```java
public class GuardPatternDemo {
    public static String categorizeNumber(Object obj) {
        return switch (obj) {
            case Integer i when i > 0  -> "Positive integer: " + i;
            case Integer i when i < 0  -> "Negative integer: " + i;
            case Integer i             -> "Zero";
            case Double d when d > 0.0 -> "Positive double: " + d;
            case Double d              -> "Non-positive double: " + d;
            case null                  -> "null value";
            default                    -> "Not a number";
        };
    }
    
    public static void processString(String str) {
        switch (str) {
            case null -> System.out.println("null string");
            case String s when s.isEmpty() -> System.out.println("Empty string");
            case String s when s.length() < 5 -> System.out.println("Short string: " + s);
            default -> System.out.println("Regular string: " + str);
        }
    }
}
```

### Null Handling in Pattern switch

```java
public class NullHandlingDemo {
    // Explicit null case
    public static String process(String str) {
        return switch (str) {
            case null -> "Was null";
            case "HELLO" -> "Hello in uppercase";
            default -> "Other value: " + str;
        };
    }
    
    // Without explicit null case - NullPointerException!
    public static String processUnsafe(String str) {
        return switch (str) {  // Throws NPE if str is null
            case "HELLO" -> "Hello in uppercase";
            default -> "Other value: " + str;
        };
    }
}
```

### Dominance and Ordering

Pattern order matters—more specific patterns must come before more general ones:

```java
public class DominanceDemo {
    // Correct ordering - specific to general
    public static String describe(Number num) {
        return switch (num) {
            case Integer i when i > 100 -> "Large integer";
            case Integer i -> "Integer";  // More specific
            case Double d -> "Double";
            case Number n -> "Some number";  // Most general
        };
    }
    
    // COMPILATION ERROR - unreachable pattern
    public static String describeWrong(Number num) {
        return switch (num) {
            case Number n -> "Some number";  // Too general - dominates others
            case Integer i -> "Integer";  // ERROR: Unreachable!
            default -> "Unknown";
        };
    }
}
```

## Sealed Classes (Java 17+)

### What are Sealed Classes?

Sealed classes restrict which classes can extend or implement them, providing controlled inheritance:

```java
// Sealed class with permitted subclasses
public sealed class Shape 
    permits Circle, Rectangle, Triangle {
    // Common shape functionality
}

// Permitted subclasses must be final, sealed, or non-sealed
final class Circle extends Shape {
    private double radius;
    // Circle implementation
}

final class Rectangle extends Shape {
    private double length, width;
    // Rectangle implementation
}

final class Triangle extends Shape {
    private double base, height;
    // Triangle implementation
}
```

### Sealed Class Rules

1. **Declare permitted subclasses** using `permits` keyword
2. **Subclasses must** be in the same module or package (if unnamed module)
3. **Subclasses must** be one of: `final`, `sealed`, or `non-sealed`
4. **Subclasses must** directly extend the sealed class

```java
// Rule 1: Declare permits
sealed class Animal permits Dog, Cat { }

// Rule 3: Subclass must be final, sealed, or non-sealed
final class Dog extends Animal { }

sealed class Cat extends Animal permits DomesticCat, WildCat { }

final class DomesticCat extends Cat { }
final class WildCat extends Cat { }
```

### Non-sealed Classes

Use `non-sealed` to allow unrestricted inheritance again:

```java
sealed class Vehicle permits Car, Truck, Motorcycle { }

final class Car extends Vehicle { }

non-sealed class Truck extends Vehicle { }

// Anyone can extend Truck now
class PickupTruck extends Truck { }
class DumpTruck extends Truck { }

final class Motorcycle extends Vehicle { }
```

### Implicit Permits (Same File)

If all permitted subclasses are in the same file, the `permits` clause is optional:

```java
// Shape.java
public sealed class Shape {
    // permits clause is implicit
}

final class Circle extends Shape {
    double radius;
}

final class Rectangle extends Shape {
    double length, width;
}
```

### Sealed Interfaces

Interfaces can also be sealed:

```java
sealed interface Expr 
    permits ConstantExpr, PlusExpr, TimesExpr, NegExpr {
    int eval();
}

record ConstantExpr(int value) implements Expr {
    public int eval() { return value; }
}

record PlusExpr(Expr left, Expr right) implements Expr {
    public int eval() { return left.eval() + right.eval(); }
}

record TimesExpr(Expr left, Expr right) implements Expr {
    public int eval() { return left.eval() * right.eval(); }
}

record NegExpr(Expr expr) implements Expr {
    public int eval() { return -expr.eval(); }
}
```

## Sealed Classes with Pattern Matching

Sealed classes combine powerfully with pattern matching for exhaustive switch expressions:

```java
sealed interface Result permits Success, Failure { }

record Success(String data) implements Result { }
record Failure(String error) implements Result { }

public class ResultProcessor {
    // Exhaustive switch - no default needed!
    public static void process(Result result) {
        switch (result) {
            case Success(String data) -> System.out.println("Success: " + data);
            case Failure(String error) -> System.out.println("Error: " + error);
            // No default needed - compiler knows all possible types
        }
    }
}
```

### Benefits of Sealed Classes with Pattern Matching

```java
sealed class Expression permits Value, Add, Multiply { }

record Value(int value) implements Expression { }
record Add(Expression left, Expression right) implements Expression { }
record Multiply(Expression left, Expression right) implements Expression { }

public class ExpressionEvaluator {
    // Compiler ensures exhaustiveness
    public static int eval(Expression expr) {
        return switch (expr) {
            case Value(int v) -> v;
            case Add(Expression l, Expression r) -> eval(l) + eval(r);
            case Multiply(Expression l, Expression r) -> eval(l) * eval(r);
            // If we add a new expression type, compiler will force us to handle it!
        };
    }
}
```

## Record Patterns (Java 21)

Record patterns allow deconstructing records in pattern matching:

```java
record Point(int x, int y) { }

public class RecordPatternDemo {
    public static void printPoint(Object obj) {
        // Deconstruct the record
        if (obj instanceof Point(int x, int y)) {
            System.out.println("Point at (" + x + ", " + y + ")");
        }
    }
    
    public static int getX(Object obj) {
        return switch (obj) {
            case Point(int x, int y) -> x;
            default -> 0;
        };
    }
}
```

### Nested Record Patterns

```java
record Point(int x, int y) { }
record Rectangle(Point topLeft, Point bottomRight) { }

public class NestedPatternDemo {
    public static void processRectangle(Object obj) {
        if (obj instanceof Rectangle(Point(int x1, int y1), Point(int x2, int y2))) {
            int width = x2 - x1;
            int height = y2 - y1;
            System.out.println("Width: " + width + ", Height: " + height);
        }
    }
}
```

## Practical Examples

### Example 1: Type-Safe JSON Processing

```java
sealed interface JsonValue 
    permits JsonObject, JsonArray, JsonString, JsonNumber, JsonBoolean, JsonNull { }

record JsonObject(Map<String, JsonValue> fields) implements JsonValue { }
record JsonArray(List<JsonValue> elements) implements JsonValue { }
record JsonString(String value) implements JsonValue { }
record JsonNumber(double value) implements JsonValue { }
record JsonBoolean(boolean value) implements JsonValue { }
record JsonNull() implements JsonValue { }

public class JsonProcessor {
    public static String stringify(JsonValue value) {
        return switch (value) {
            case JsonObject(var fields) -> "{" + stringifyObject(fields) + "}";
            case JsonArray(var elements) -> "[" + stringifyArray(elements) + "]";
            case JsonString(var str) -> "\"" + str + "\"";
            case JsonNumber(var num) -> String.valueOf(num);
            case JsonBoolean(var bool) -> String.valueOf(bool);
            case JsonNull() -> "null";
        };
    }
    
    private static String stringifyObject(Map<String, JsonValue> fields) {
        return fields.entrySet().stream()
            .map(e -> "\"" + e.getKey() + "\":" + stringify(e.getValue()))
            .collect(Collectors.joining(","));
    }
    
    private static String stringifyArray(List<JsonValue> elements) {
        return elements.stream()
            .map(JsonProcessor::stringify)
            .collect(Collectors.joining(","));
    }
}
```

### Example 2: Expression Evaluator

```java
sealed interface Expr permits Constant, Negate, Add, Multiply { }

record Constant(int value) implements Expr { }
record Negate(Expr expr) implements Expr { }
record Add(Expr left, Expr right) implements Expr { }
record Multiply(Expr left, Expr right) implements Expr { }

public class Calculator {
    public static int evaluate(Expr expr) {
        return switch (expr) {
            case Constant(int value) -> value;
            case Negate(Expr e) -> -evaluate(e);
            case Add(Expr left, Expr right) -> evaluate(left) + evaluate(right);
            case Multiply(Expr left, Expr right) -> evaluate(left) * evaluate(right);
        };
    }
    
    public static void main(String[] args) {
        // (5 + 3) * -2
        Expr expr = new Multiply(
            new Add(new Constant(5), new Constant(3)),
            new Negate(new Constant(2))
        );
        System.out.println(evaluate(expr));  // -16
    }
}
```

## Best Practices

### 1. Use Pattern Matching to Reduce Boilerplate

```java
// Bad - verbose
if (obj instanceof String) {
    String s = (String) obj;
    process(s);
}

// Good - concise
if (obj instanceof String s) {
    process(s);
}
```

### 2. Leverage Guards for Conditional Logic

```java
// Good use of guards
public String categorize(Object obj) {
    return switch (obj) {
        case Integer i when i > 0 -> "positive";
        case Integer i when i < 0 -> "negative";
        case Integer i -> "zero";
        default -> "not an integer";
    };
}
```

### 3. Use Sealed Classes for Closed Hierarchies

```java
// Good - API clearly documents all possible shapes
sealed interface Shape permits Circle, Rectangle, Triangle {
    double area();
}
```

### 4. Combine Sealed Classes with Records

```java
// Excellent pattern for algebraic data types
sealed interface Option<T> permits Some, None { }

record Some<T>(T value) implements Option<T> { }
record None<T>() implements Option<T> { }
```

## Summary

- **Pattern Matching for instanceof** combines type testing and casting in one concise expression
- Pattern variables have **flow-scoped** visibility based on definite assignment
- **Pattern Matching for switch** (Java 21) enables switching on any type with patterns and guards
- **Sealed Classes** restrict inheritance to a known set of subclasses
- Sealed classes must use **permits** to declare allowed subclasses (unless in same file)
- Subclasses of sealed classes must be **final**, **sealed**, or **non-sealed**
- **Sealed interfaces** work similarly to sealed classes
- Sealed classes with pattern matching enable **exhaustive switch** expressions
- **Record patterns** (Java 21) allow deconstructing records in patterns
- These features together provide **type safety**, **exhaustiveness checking**, and **reduced boilerplate**
