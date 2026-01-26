# Module 6.1: Inheritance

## 📚 Table of Contents
1. [Introduction to Inheritance](#introduction-to-inheritance)
2. [The `extends` Keyword](#the-extends-keyword)
3. [Method Overriding](#method-overriding)
4. [The `super` Keyword](#the-super-keyword)
5. [Constructor Chaining](#constructor-chaining)
6. [The Object Class](#the-object-class)
7. [Final Classes and Methods](#final-classes-and-methods)
8. [Best Practices](#best-practices)
9. [Common Pitfalls](#common-pitfalls)

---

## Introduction to Inheritance

Inheritance allows a class to acquire properties and behaviors from another class.

### Benefits of Inheritance

- **Code Reuse** - Inherit existing functionality
- **Extensibility** - Add new features to existing classes
- **Polymorphism** - Objects can take multiple forms
- **Hierarchy** - Create logical class relationships

### IS-A Relationship

```java
class Animal { }
class Dog extends Animal { }  // Dog IS-A Animal
class Cat extends Animal { }  // Cat IS-A Animal
```

---

## The `extends` Keyword

### Basic Inheritance

```java
// Parent/Super/Base class
class Animal {
    String name;
    
    void eat() {
        System.out.println(name + " is eating");
    }
    
    void sleep() {
        System.out.println(name + " is sleeping");
    }
}

// Child/Sub/Derived class
class Dog extends Animal {
    void bark() {
        System.out.println(name + " is barking");
    }
}

Dog dog = new Dog();
dog.name = "Buddy";
dog.eat();    // Inherited from Animal
dog.sleep();  // Inherited from Animal
dog.bark();   // Defined in Dog
```

### Multilevel Inheritance

```java
class Animal {
    void breathe() {
        System.out.println("Breathing");
    }
}

class Mammal extends Animal {
    void feedMilk() {
        System.out.println("Feeding milk");
    }
}

class Dog extends Mammal {
    void bark() {
        System.out.println("Barking");
    }
}

Dog dog = new Dog();
dog.breathe();  // From Animal
dog.feedMilk(); // From Mammal
dog.bark();     // From Dog
```

### Java Inheritance Rules

- Java supports **single inheritance** only (one superclass)
- Java does NOT support **multiple inheritance** (multiple superclasses)
- Java supports **multilevel inheritance**
- All classes inherit from `Object` implicitly

```java
// Valid - single inheritance
class B extends A { }

// Invalid - multiple inheritance
// class C extends A, B { }  // Compilation error

// Valid - multilevel inheritance
class A { }
class B extends A { }
class C extends B { }  // C -> B -> A
```

---

## Method Overriding

Method overriding allows a subclass to provide a specific implementation for a method inherited from the superclass.

### Basic Overriding

```java
class Animal {
    void makeSound() {
        System.out.println("Animal makes a sound");
    }
}

class Dog extends Animal {
    @Override  // Optional but recommended
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

Animal animal = new Animal();
animal.makeSound();  // Animal makes a sound

Dog dog = new Dog();
dog.makeSound();  // Dog barks

Cat cat = new Cat();
cat.makeSound();  // Cat meows
```

### Overriding Rules

1. **Method signature must match** (name and parameters)
2. **Return type** must be same or covariant (subtype)
3. **Access modifier** cannot be more restrictive
4. **Cannot override** final methods
5. **Cannot override** static methods (hiding, not overriding)
6. **Can throw** same, fewer, or narrower exceptions

```java
class Parent {
    protected Number getValue() {
        return 10;
    }
    
    void method1() throws IOException { }
}

class Child extends Parent {
    // Valid - covariant return type
    @Override
    public Integer getValue() {  // Integer is subtype of Number
        return 20;
    }
    
    // Valid - fewer exceptions
    @Override
    void method1() { }  // Doesn't throw exception
    
    // Invalid - more restrictive access
    // @Override
    // private void method1() { }  // Error
}
```

### @Override Annotation

```java
class Parent {
    void display() {
        System.out.println("Parent");
    }
}

class Child extends Parent {
    @Override
    void display() {  // Annotation ensures correct overriding
        System.out.println("Child");
    }
    
    // @Override
    // void Display() { }  // Compilation error - method not found in parent
}
```

---

## The `super` Keyword

`super` refers to the parent class.

### Accessing Parent Methods

```java
class Parent {
    void display() {
        System.out.println("Parent display");
    }
}

class Child extends Parent {
    @Override
    void display() {
        super.display();  // Call parent's display()
        System.out.println("Child display");
    }
}

Child child = new Child();
child.display();
// Output:
// Parent display
// Child display
```

### Accessing Parent Fields

```java
class Parent {
    int value = 10;
}

class Child extends Parent {
    int value = 20;
    
    void printValues() {
        System.out.println("Child value: " + value);         // 20
        System.out.println("Child value: " + this.value);    // 20
        System.out.println("Parent value: " + super.value);  // 10
    }
}
```

### Calling Parent Constructor

```java
class Parent {
    int x;
    
    Parent(int x) {
        this.x = x;
    }
}

class Child extends Parent {
    int y;
    
    Child(int x, int y) {
        super(x);  // Must be first statement
        this.y = y;
    }
}
```

---

## Constructor Chaining

Constructors are called in order from parent to child.

### Implicit super()

```java
class Parent {
    Parent() {
        System.out.println("Parent constructor");
    }
}

class Child extends Parent {
    Child() {
        // super(); implicitly called
        System.out.println("Child constructor");
    }
}

Child child = new Child();
// Output:
// Parent constructor
// Child constructor
```

### Explicit super()

```java
class Parent {
    int value;
    
    Parent(int value) {
        this.value = value;
        System.out.println("Parent: " + value);
    }
}

class Child extends Parent {
    Child() {
        super(10);  // Explicit call to parent constructor
        System.out.println("Child");
    }
}

Child child = new Child();
// Output:
// Parent: 10
// Child
```

### Constructor Chaining Rules

1. `super()` or `this()` must be **first statement** in constructor
2. If no explicit `super()` or `this()`, compiler inserts `super()`
3. Cannot use both `super()` and `this()` in same constructor

```java
class Parent {
    Parent(int value) { }
}

class Child extends Parent {
    Child() {
        // super();  // Compilation error - Parent has no no-arg constructor
        super(10);  // Must explicitly call Parent(int)
    }
}
```

---

## The Object Class

All classes inherit from `Object` implicitly.

### Common Object Methods

```java
class Person {
    String name;
    int age;
    
    // Override toString()
    @Override
    public String toString() {
        return "Person{name='" + name + "', age=" + age + "}";
    }
    
    // Override equals()
    @Override
    public boolean equals(Object obj) {
        if (this == obj) return true;
        if (obj == null || getClass() != obj.getClass()) return false;
        Person person = (Person) obj;
        return age == person.age && name.equals(person.name);
    }
    
    // Override hashCode()
    @Override
    public int hashCode() {
        return Objects.hash(name, age);
    }
}
```

### Object Class Methods

| Method | Purpose |
|--------|---------|
| `toString()` | String representation of object |
| `equals(Object)` | Compare objects for equality |
| `hashCode()` | Hash code for collections |
| `getClass()` | Get runtime class |
| `clone()` | Create a copy |
| `finalize()` | Called before garbage collection (deprecated) |

---

## Final Classes and Methods

### Final Methods

Final methods cannot be overridden.

```java
class Parent {
    final void display() {
        System.out.println("Cannot override this");
    }
}

class Child extends Parent {
    // @Override
    // void display() { }  // Compilation error - cannot override final method
}
```

### Final Classes

Final classes cannot be extended.

```java
final class Utility {
    static int add(int a, int b) {
        return a + b;
    }
}

// class MyUtility extends Utility { }  // Compilation error - cannot extend final class
```

### Real-World Examples

```java
// String is final
final class String { }

// Integer is final
final class Integer { }

// Math class methods are static (class has private constructor)
public final class Math {
    private Math() { }
    public static int max(int a, int b) { return (a >= b) ? a : b; }
}
```

---

## Best Practices

### 1. Use Composition Over Inheritance

```java
// Bad - inheritance for code reuse
class Employee extends ArrayList<String> {
    // Employee IS-A ArrayList? No!
}

// Good - composition
class Employee {
    private List<String> skills = new ArrayList<>();  // HAS-A relationship
}
```

### 2. Design for Inheritance or Prohibit It

```java
// Either make it final
public final class Utility { }

// Or design it for inheritance
public class Extensible {
    // Protected methods for subclasses
    protected void customizeLogic() { }
}
```

### 3. Always Use @Override

```java
class Parent {
    void process(String data) { }
}

class Child extends Parent {
    @Override  // Catches typos and signature mismatches
    void process(String data) { }
    
    // Without @Override, this would be a new method (not override)
    // void Process(String data) { }  // Typo - P is capital
}
```

### 4. Document Inheritance Contracts

```java
/**
 * Override this method to customize validation logic.
 * Default implementation validates length.
 * 
 * @param input the input to validate
 * @return true if valid, false otherwise
 */
protected boolean validate(String input) {
    return input != null && input.length() > 0;
}
```

---

## Common Pitfalls

### 1. Forgetting super() Call

```java
class Parent {
    Parent(int value) { }
}

class Child extends Parent {
    Child() {
        // super(10);  // Missing - compilation error
    }
}
```

### 2. Overriding vs Overloading Confusion

```java
class Parent {
    void method(int x) { }
}

class Child extends Parent {
    // This is overloading, not overriding
    void method(String x) { }
    
    // This is overriding
    @Override
    void method(int x) { }
}
```

### 3. Calling Overridden Method from Constructor

```java
class Parent {
    Parent() {
        init();  // Dangerous - calls child's overridden method
    }
    
    void init() {
        System.out.println("Parent init");
    }
}

class Child extends Parent {
    int value = 10;
    
    @Override
    void init() {
        System.out.println("Value: " + value);  // Prints 0, not 10!
    }
}

Child child = new Child();
// Output: Value: 0 (field not yet initialized when parent constructor runs)
```

### 4. Hiding vs Overriding

```java
class Parent {
    static void staticMethod() {
        System.out.println("Parent static");
    }
    
    void instanceMethod() {
        System.out.println("Parent instance");
    }
}

class Child extends Parent {
    // Hiding (not overriding) - static methods
    static void staticMethod() {
        System.out.println("Child static");
    }
    
    // Overriding - instance methods
    @Override
    void instanceMethod() {
        System.out.println("Child instance");
    }
}

Parent p = new Child();
p.staticMethod();    // Parent static (decided at compile-time)
p.instanceMethod();  // Child instance (decided at runtime)
```

---

## Summary

### Inheritance
- **Syntax:** `class Child extends Parent`
- **Purpose:** Code reuse, extensibility, polymorphism
- **Limitation:** Single inheritance only

### Method Overriding
- Subclass provides specific implementation
- Must match signature and return type (or covariant)
- Use `@Override` annotation

### super Keyword
- Access parent's methods, fields, and constructors
- `super()` must be first in constructor

### Object Class
- All classes inherit from Object
- Override `toString()`, `equals()`, `hashCode()` as needed

### Final
- **Final methods:** Cannot be overridden
- **Final classes:** Cannot be extended

---

## Practice Questions

Ready to test your knowledge? Proceed to [Inheritance Practice Questions](12-practice-questions.md)!

---

**Next:** [Practice Questions - Inheritance](12-practice-questions.md)  
**Previous:** [Varargs and Nested Classes](../module-05/11-variable-arguments.md)

---

**Good luck!** ☕
