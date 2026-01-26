# Module 5.3: Variable Arguments and Nested Classes

## 📚 Table of Contents
1. [Variable Arguments (Varargs)](#variable-arguments-varargs)
2. [Nested Classes Overview](#nested-classes-overview)
3. [Static Nested Classes](#static-nested-classes)
4. [Inner Classes](#inner-classes)
5. [Local Classes](#local-classes)
6. [Anonymous Classes](#anonymous-classes)
7. [Best Practices](#best-practices)
8. [Common Pitfalls](#common-pitfalls)

---

## Variable Arguments (Varargs)

Varargs allow methods to accept zero or more arguments of a specified type.

### Basic Varargs Syntax

```java
public void printNumbers(int... numbers) {
    for (int num : numbers) {
        System.out.println(num);
    }
}

printNumbers();              // 0 arguments
printNumbers(1);             // 1 argument
printNumbers(1, 2, 3);       // 3 arguments
printNumbers(1, 2, 3, 4, 5); // 5 arguments
```

### Varargs as Array

```java
public int sum(int... values) {
    int total = 0;
    for (int value : values) {
        total += value;
    }
    return total;
}

// Can also pass an array
int[] numbers = {1, 2, 3, 4, 5};
int result = sum(numbers);  // Valid
```

### Varargs with Other Parameters

```java
// Varargs must be the last parameter
public void log(String level, String... messages) {
    System.out.println("[" + level + "]");
    for (String message : messages) {
        System.out.println(message);
    }
}

log("INFO", "Application started");
log("ERROR", "Connection failed", "Retrying...", "Success");
```

### Varargs Rules

1. Only one varargs parameter per method
2. Must be the last parameter
3. Treated as an array internally

```java
// Valid
public void method1(int... numbers) { }
public void method2(String name, int... scores) { }

// Invalid
// public void method3(int... numbers, String name) { }  // varargs must be last
// public void method4(int... numbers, String... names) { }  // only one varargs
```

### Varargs vs Array

```java
// Varargs
public void printVarargs(int... numbers) {
    System.out.println("Length: " + numbers.length);
}

// Array
public void printArray(int[] numbers) {
    System.out.println("Length: " + numbers.length);
}

// Calling
printVarargs(1, 2, 3);           // Varargs - convenient
printArray(new int[]{1, 2, 3});  // Array - explicit
```

---

## Nested Classes Overview

Nested classes are classes defined within another class.

### Four Types of Nested Classes

1. **Static Nested Classes** - Static members of outer class
2. **Inner Classes** - Non-static members of outer class
3. **Local Classes** - Defined inside a method
4. **Anonymous Classes** - Unnamed classes for one-time use

---

## Static Nested Classes

Static nested classes are associated with the outer class, not instances.

### Declaration and Usage

```java
public class Outer {
    private static int outerStaticField = 10;
    private int outerInstanceField = 20;
    
    // Static nested class
    static class StaticNested {
        void display() {
            // Can access outer static members
            System.out.println("Outer static: " + outerStaticField);
            
            // Cannot access outer instance members directly
            // System.out.println(outerInstanceField);  // Error
        }
    }
}

// Creating static nested class instance
Outer.StaticNested nested = new Outer.StaticNested();
nested.display();
```

### Use Cases for Static Nested Classes

```java
public class LinkedList {
    private Node head;
    
    // Static nested class for list nodes
    private static class Node {
        int data;
        Node next;
        
        Node(int data) {
            this.data = data;
        }
    }
    
    public void add(int data) {
        Node newNode = new Node(data);
        if (head == null) {
            head = newNode;
        } else {
            // Add to end
        }
    }
}
```

---

## Inner Classes

Inner classes (non-static nested classes) have access to all members of the outer class.

### Declaration and Usage

```java
public class Outer {
    private int outerField = 10;
    
    // Inner class
    class Inner {
        private int innerField = 20;
        
        void display() {
            // Can access outer instance members
            System.out.println("Outer field: " + outerField);
            System.out.println("Inner field: " + innerField);
        }
    }
}

// Creating inner class instance (requires outer instance)
Outer outer = new Outer();
Outer.Inner inner = outer.new Inner();
inner.display();
```

### Inner Class Accessing Outer Members

```java
public class Outer {
    private String name = "Outer";
    
    class Inner {
        private String name = "Inner";
        
        void printNames() {
            System.out.println(name);           // Inner's name
            System.out.println(this.name);      // Inner's name
            System.out.println(Outer.this.name); // Outer's name
        }
    }
}
```

### Use Cases for Inner Classes

```java
public class ArrayList<E> {
    private Object[] elements;
    private int size;
    
    // Inner class for iterator
    private class Itr implements Iterator<E> {
        int cursor = 0;
        
        public boolean hasNext() {
            return cursor < size;  // Access outer's size
        }
        
        public E next() {
            return (E) elements[cursor++];  // Access outer's elements
        }
    }
    
    public Iterator<E> iterator() {
        return new Itr();
    }
}
```

---

## Local Classes

Local classes are defined inside a method or block.

### Declaration and Usage

```java
public class Outer {
    public void method() {
        final int localVar = 30;
        
        // Local class
        class Local {
            void display() {
                System.out.println("Local var: " + localVar);
            }
        }
        
        Local local = new Local();
        local.display();
    }
}
```

### Accessing Local Variables

```java
public void calculate(int x) {
    int y = 10;  // Effectively final
    
    class Calculator {
        int compute() {
            return x + y;  // Can access effectively final local variables
        }
    }
    
    Calculator calc = new Calculator();
    System.out.println(calc.compute());
    
    // y = 20;  // Would make y not effectively final - error in Calculator
}
```

### Use Cases for Local Classes

```java
public List<String> filterNames(List<String> names, String prefix) {
    // Local class for filtering logic
    class NameFilter {
        boolean matches(String name) {
            return name.startsWith(prefix);
        }
    }
    
    NameFilter filter = new NameFilter();
    List<String> result = new ArrayList<>();
    for (String name : names) {
        if (filter.matches(name)) {
            result.add(name);
        }
    }
    return result;
}
```

---

## Anonymous Classes

Anonymous classes are unnamed classes used for one-time implementations.

### Anonymous Class Syntax

```java
// Interface
interface Greeting {
    void greet(String name);
}

// Anonymous class implementation
Greeting greeting = new Greeting() {
    @Override
    public void greet(String name) {
        System.out.println("Hello, " + name);
    }
};

greeting.greet("Alice");  // Hello, Alice
```

### Anonymous Class from Abstract Class

```java
abstract class Animal {
    abstract void makeSound();
}

Animal dog = new Animal() {
    @Override
    void makeSound() {
        System.out.println("Woof!");
    }
};

dog.makeSound();  // Woof!
```

### Anonymous Class with Constructor Arguments

```java
abstract class Shape {
    String color;
    
    Shape(String color) {
        this.color = color;
    }
    
    abstract double area();
}

Shape circle = new Shape("Red") {  // Pass argument to superclass constructor
    double radius = 5;
    
    @Override
    double area() {
        return Math.PI * radius * radius;
    }
};
```

### Use Cases - Event Handlers

```java
button.setOnClickListener(new OnClickListener() {
    @Override
    public void onClick(View v) {
        System.out.println("Button clicked!");
    }
});

// Or with lambda (Java 8+)
button.setOnClickListener(v -> System.out.println("Button clicked!"));
```

---

## Best Practices

### 1. Choose the Right Nested Class Type

```java
// Static nested class - for utility or helper classes
public class OuterClass {
    static class Builder {
        // Builder pattern
    }
}

// Inner class - when you need access to outer instance
public class OuterClass {
    class Iterator {
        // Needs access to outer's data
    }
}

// Local class - for limited scope logic
public void method() {
    class Helper {
        // Only used in this method
    }
}

// Anonymous class - for one-time implementations
Runnable task = new Runnable() {
    public void run() {
        // Single use
    }
};
```

### 2. Prefer Lambdas for Functional Interfaces

```java
// Before Java 8 - anonymous class
Comparator<String> comparator = new Comparator<String>() {
    public int compare(String s1, String s2) {
        return s1.length() - s2.length();
    }
};

// Java 8+ - lambda expression (cleaner)
Comparator<String> lambdaComparator = (s1, s2) -> s1.length() - s2.length();
```

### 3. Keep Nested Classes Private When Possible

```java
public class ArrayList {
    // Private inner class - implementation detail
    private class Itr implements Iterator {
        // ...
    }
}
```

### 4. Use Varargs Judiciously

```java
// Good use case
public String format(String template, Object... args) {
    return String.format(template, args);
}

// Be careful with ambiguity
public void method(String... args) { }
public void method(String arg) { }  // Avoid - can cause confusion
```

---

## Common Pitfalls

### 1. Varargs Ambiguity

```java
public void print(int... numbers) {
    System.out.println("Varargs: int");
}

public void print(int number) {
    System.out.println("Single: int");
}

print(10);  // Calls single parameter version (more specific)
print(10, 20);  // Calls varargs version
```

### 2. Varargs with Null

```java
public void process(String... args) {
    System.out.println("Length: " + args.length);
}

process(null);  // NullPointerException - treats null as array, not empty varargs
process((String) null);  // OK - array with one null element
process();  // OK - empty array
```

### 3. Inner Class Without Outer Instance

```java
public class Outer {
    class Inner { }
}

// Wrong
// Outer.Inner inner = new Outer.Inner();  // Error - needs outer instance

// Correct
Outer outer = new Outer();
Outer.Inner inner = outer.new Inner();
```

### 4. Accessing Modified Local Variables

```java
public void method() {
    int x = 10;
    
    class Local {
        void display() {
            System.out.println(x);  // OK - x is effectively final
        }
    }
    
    // x = 20;  // Error - would make x not effectively final
}
```

### 5. Anonymous Class Limitations

```java
// Cannot have constructors
Runnable r = new Runnable() {
    // public Runnable() { }  // Error - anonymous classes can't have constructors
    
    @Override
    public void run() {
        System.out.println("Running");
    }
};

// Cannot implement multiple interfaces
// Cannot extend a class and implement an interface simultaneously
```

---

## Summary

### Varargs
- **Syntax:** `type... paramName`
- **Rules:** Only one varargs, must be last parameter
- **Usage:** Treated as array, allows 0+ arguments

### Nested Classes

| Type | Keyword | Access to Outer | Instantiation |
|------|---------|-----------------|---------------|
| **Static Nested** | static | Static members only | `new Outer.Nested()` |
| **Inner** | None | All members | `outer.new Inner()` |
| **Local** | In method | Effectively final locals | Inside method only |
| **Anonymous** | No name | Depends on scope | Inline with `new` |

### When to Use
- **Static Nested:** Helper/utility classes
- **Inner:** Iterator, event listeners
- **Local:** Limited scope logic
- **Anonymous:** One-time implementations (consider lambdas)

---

## Practice Questions

Ready to test your knowledge? Proceed to [Varargs and Nested Classes Practice](11-practice-questions.md)!

---

**Next:** [Practice Questions - Varargs and Nested Classes](11-practice-questions.md)  
**Previous:** [Methods and Parameters Practice](10-practice-questions.md)

---

**Good luck!** ☕
