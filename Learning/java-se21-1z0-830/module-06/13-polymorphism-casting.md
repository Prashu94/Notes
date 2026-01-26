# Polymorphism and Type Casting

## Introduction

Polymorphism is one of the four fundamental principles of Object-Oriented Programming (OOP), alongside encapsulation, inheritance, and abstraction. The term "polymorphism" comes from Greek, meaning "many forms." In Java, polymorphism allows objects to take multiple forms and enables code to work with objects at different levels of abstraction.

## Understanding Polymorphism

### What is Polymorphism?

Polymorphism in Java allows a single action to behave differently based on the object that performs it. There are two types of polymorphism in Java:

1. **Compile-time Polymorphism (Static Binding)**: Achieved through method overloading
2. **Runtime Polymorphism (Dynamic Binding)**: Achieved through method overriding

### Runtime Polymorphism

Runtime polymorphism occurs when a superclass reference variable points to a subclass object. The method that gets executed is determined at runtime based on the actual object type, not the reference type.

```java
class Animal {
    void makeSound() {
        System.out.println("Animal makes a sound");
    }
}

class Dog extends Animal {
    @Override
    void makeSound() {
        System.out.println("Dog barks");
    }
}

class Cat extends Animal {
    @Override
    void makeSound() {
        System.out.println("Cat meows");
    }
}

public class PolymorphismDemo {
    public static void main(String[] args) {
        Animal animal1 = new Dog();  // Polymorphism
        Animal animal2 = new Cat();  // Polymorphism
        
        animal1.makeSound();  // Outputs: Dog barks
        animal2.makeSound();  // Outputs: Cat meows
    }
}
```

### Benefits of Polymorphism

1. **Code Reusability**: Write generic code that works with parent class references
2. **Flexibility**: Add new subclasses without modifying existing code
3. **Maintainability**: Centralize common behavior in parent classes
4. **Loose Coupling**: Depend on abstractions rather than concrete implementations

## Type Casting

Type casting is the process of converting an object from one type to another. In Java, there are two types of casting with object references:

### Upcasting (Widening)

Upcasting is converting a subclass reference to a superclass reference. It's implicit and always safe.

```java
Dog dog = new Dog();
Animal animal = dog;  // Upcasting (implicit)
```

**Key Points about Upcasting:**
- Always safe and never fails
- No explicit cast required
- Loss of access to subclass-specific members
- The object itself doesn't change, only the reference type

```java
class Vehicle {
    void start() {
        System.out.println("Vehicle starting");
    }
}

class Car extends Vehicle {
    void start() {
        System.out.println("Car starting");
    }
    
    void playMusic() {
        System.out.println("Playing music");
    }
}

public class UpcastingDemo {
    public static void main(String[] args) {
        Car car = new Car();
        Vehicle vehicle = car;  // Upcasting
        
        vehicle.start();  // Outputs: Car starting (polymorphism)
        // vehicle.playMusic();  // Compilation error! Vehicle doesn't have playMusic()
        
        // Even though we can't call playMusic() through vehicle reference,
        // the actual object is still a Car
    }
}
```

### Downcasting (Narrowing)

Downcasting is converting a superclass reference to a subclass reference. It requires an explicit cast and can fail at runtime.

```java
Animal animal = new Dog();
Dog dog = (Dog) animal;  // Downcasting (explicit cast required)
```

**Key Points about Downcasting:**
- Requires explicit cast syntax
- Can throw `ClassCastException` at runtime if the cast is invalid
- Grants access to subclass-specific members
- Should be preceded by an `instanceof` check

```java
public class DowncastingDemo {
    public static void main(String[] args) {
        Animal animal = new Dog();
        
        // Safe downcasting
        if (animal instanceof Dog) {
            Dog dog = (Dog) animal;
            dog.makeSound();  // Now we can access Dog-specific methods
        }
        
        // Unsafe downcasting - will throw ClassCastException
        Animal animal2 = new Cat();
        // Dog dog2 = (Dog) animal2;  // Runtime error!
    }
}
```

## The instanceof Operator

The `instanceof` operator tests whether an object is an instance of a specific class or implements a specific interface.

### Basic instanceof Usage

```java
class Shape { }
class Circle extends Shape { }
class Rectangle extends Shape { }

public class InstanceofDemo {
    public static void main(String[] args) {
        Shape shape = new Circle();
        
        System.out.println(shape instanceof Circle);     // true
        System.out.println(shape instanceof Shape);      // true
        System.out.println(shape instanceof Rectangle);  // false
        System.out.println(shape instanceof Object);     // true (all classes extend Object)
        
        // instanceof returns false for null
        Shape nullShape = null;
        System.out.println(nullShape instanceof Shape);  // false
    }
}
```

### instanceof with Interfaces

```java
interface Drawable {
    void draw();
}

class Square implements Drawable {
    public void draw() {
        System.out.println("Drawing square");
    }
}

public class InterfaceInstanceofDemo {
    public static void main(String[] args) {
        Drawable drawable = new Square();
        
        System.out.println(drawable instanceof Drawable);  // true
        System.out.println(drawable instanceof Square);    // true
        System.out.println(drawable instanceof Object);    // true
    }
}
```

## Pattern Matching for instanceof (Java 16+)

Java 16 introduced pattern matching for `instanceof`, which simplifies the common pattern of testing a type and then casting.

### Traditional instanceof with Casting

```java
// Before Java 16
public void processShape(Shape shape) {
    if (shape instanceof Circle) {
        Circle circle = (Circle) shape;  // Explicit cast
        double radius = circle.getRadius();
        System.out.println("Circle radius: " + radius);
    }
}
```

### Pattern Matching instanceof

```java
// Java 16+
public void processShape(Shape shape) {
    if (shape instanceof Circle circle) {  // Pattern variable 'circle'
        double radius = circle.getRadius();  // No cast needed!
        System.out.println("Circle radius: " + radius);
    }
}
```

### Scope of Pattern Variables

```java
public void checkShape(Shape shape) {
    if (shape instanceof Circle circle) {
        System.out.println("Radius: " + circle.getRadius());
        // 'circle' is in scope here
    }
    // 'circle' is NOT in scope here
    
    // Pattern variable in negation
    if (!(shape instanceof Circle circle)) {
        // 'circle' is NOT in scope here (condition is negated)
    } else {
        // 'circle' IS in scope here
        System.out.println("Radius: " + circle.getRadius());
    }
    
    // Pattern variable with logical AND
    if (shape instanceof Circle circle && circle.getRadius() > 10) {
        // 'circle' is in scope because instanceof must be true
        System.out.println("Large circle");
    }
    
    // ILLEGAL: Pattern variable with logical OR
    // if (shape instanceof Circle circle || circle.getRadius() > 10) {
    //     // Compile error! circle might not be initialized
    // }
}
```

### Complex Pattern Matching Examples

```java
public class PatternMatchingDemo {
    public static void processObject(Object obj) {
        // Multiple patterns with different types
        if (obj instanceof String str) {
            System.out.println("String length: " + str.length());
        } else if (obj instanceof Integer num) {
            System.out.println("Integer value: " + num);
        } else if (obj instanceof List<?> list) {
            System.out.println("List size: " + list.size());
        }
        
        // Pattern matching in complex conditions
        if (obj instanceof String str && str.length() > 5) {
            System.out.println("Long string: " + str);
        }
        
        // Pattern matching with null check
        if (obj != null && obj instanceof String str) {
            System.out.println("Non-null string: " + str);
        }
    }
    
    // Pattern matching in return statements
    public static int getLength(Object obj) {
        return obj instanceof String str ? str.length() : -1;
    }
}
```

## Common Pitfalls and Best Practices

### Pitfall 1: ClassCastException

```java
Animal animal = new Cat();
Dog dog = (Dog) animal;  // ClassCastException at runtime!
```

**Best Practice**: Always use `instanceof` before downcasting

```java
Animal animal = new Cat();
if (animal instanceof Dog) {
    Dog dog = (Dog) animal;
    // Safe to use dog here
}
```

### Pitfall 2: Unnecessary Casting

```java
// Unnecessary - upcasting is automatic
Animal animal = (Animal) new Dog();

// Better
Animal animal = new Dog();
```

### Pitfall 3: Casting and Method Invocation

```java
class Parent {
    void display() { System.out.println("Parent"); }
}

class Child extends Parent {
    void display() { System.out.println("Child"); }
    void childMethod() { System.out.println("Child method"); }
}

public class CastingMethodDemo {
    public static void main(String[] args) {
        Parent parent = new Child();
        parent.display();  // Outputs: Child (polymorphism)
        
        // To call childMethod, we need to downcast
        ((Child) parent).childMethod();  // Outputs: Child method
        
        // Or better:
        if (parent instanceof Child child) {
            child.childMethod();
        }
    }
}
```

### Best Practice: Prefer Polymorphism over Casting

```java
// Avoid this
public void process(Animal animal) {
    if (animal instanceof Dog) {
        ((Dog) animal).bark();
    } else if (animal instanceof Cat) {
        ((Cat) animal).meow();
    }
}

// Better - use polymorphism
abstract class Animal {
    abstract void makeSound();
}

class Dog extends Animal {
    void makeSound() { System.out.println("Bark"); }
}

class Cat extends Animal {
    void makeSound() { System.out.println("Meow"); }
}

public void process(Animal animal) {
    animal.makeSound();  // Polymorphism!
}
```

## Dynamic Method Dispatch

Dynamic method dispatch is the mechanism by which Java implements runtime polymorphism. The method to be called is determined at runtime based on the actual object type.

```java
class Shape {
    double area() {
        return 0.0;
    }
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
}

public class DynamicDispatchDemo {
    public static void printArea(Shape shape) {
        // Which area() method gets called is determined at runtime
        System.out.println("Area: " + shape.area());
    }
    
    public static void main(String[] args) {
        Shape circle = new Circle(5.0);
        Shape rectangle = new Rectangle(4.0, 6.0);
        
        printArea(circle);     // Calls Circle's area()
        printArea(rectangle);  // Calls Rectangle's area()
    }
}
```

## Casting with Arrays

```java
class Animal { }
class Dog extends Animal { }
class Cat extends Animal { }

public class ArrayCastingDemo {
    public static void main(String[] args) {
        // Array upcasting
        Dog[] dogs = new Dog[5];
        Animal[] animals = dogs;  // Legal - covariance
        
        // Danger: ArrayStoreException at runtime
        // animals[0] = new Cat();  // Compiles but throws ArrayStoreException!
        
        // The array "remembers" it's actually a Dog array
        animals[0] = new Dog();  // OK
    }
}
```

## Summary

- **Polymorphism** allows objects to take multiple forms and enables writing flexible, reusable code
- **Upcasting** (subclass to superclass) is implicit and always safe
- **Downcasting** (superclass to subclass) requires explicit casting and can fail at runtime
- Always use **instanceof** to check types before downcasting
- **Pattern matching for instanceof** (Java 16+) simplifies type checking and casting
- Pattern variables have specific **scope rules** based on control flow
- Prefer **polymorphism** over type checking and casting when possible
- **Dynamic method dispatch** determines which overridden method to call at runtime
- Be cautious with **array covariance** to avoid `ArrayStoreException`
