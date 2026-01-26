# Module 6: Abstract Classes - Practice Questions

## Practice Questions (20)

### Question 1
Which statement about abstract classes is TRUE?
```java
abstract class Animal {
    abstract void makeSound();
}
```
A) You can create an instance of Animal using `new Animal()`  
B) Animal must have at least one abstract method  
C) All methods in Animal must be abstract  
D) You cannot instantiate Animal directly

**Answer: D) You cannot instantiate Animal directly**

**Explanation**: Abstract classes cannot be instantiated. You must create a concrete subclass that implements all abstract methods. Option B is false because abstract classes can have zero abstract methods (they can be abstract just to prevent instantiation). Option C is false because abstract classes can have both abstract and concrete methods.

---

### Question 2
What is the output?
```java
abstract class Shape {
    Shape() {
        System.out.print("Shape ");
    }
    abstract double area();
}

class Circle extends Shape {
    Circle() {
        System.out.print("Circle ");
    }
    
    double area() {
        return 3.14;
    }
}

public class Test {
    public static void main(String[] args) {
        Shape s = new Circle();
    }
}
```
A) Circle  
B) Shape  
C) Shape Circle  
D) Compilation error

**Answer: C) Shape Circle**

**Explanation**: Abstract classes can have constructors. When you create a `Circle` instance, the parent `Shape` constructor is called first (implicitly via `super()`), printing "Shape ", then the `Circle` constructor executes, printing "Circle ". Constructors in abstract classes are called when subclass objects are instantiated.

---

### Question 3
Which code will NOT compile?
A)
```java
abstract class A {
    abstract void method();
}
```
B)
```java
abstract class B {
    void method() {
        System.out.println("Implemented");
    }
}
```
C)
```java
abstract class C {
    private abstract void method();
}
```
D)
```java
abstract class D {
    static void method() {
        System.out.println("Static");
    }
}
```

**Answer: C)**

**Explanation**: Abstract methods cannot be private because they must be accessible to subclasses for overriding. Option A is valid (abstract class with abstract method), Option B is valid (abstract class can have concrete methods), and Option D is valid (abstract classes can have static methods).

---

### Question 4
What happens when you compile and run this code?
```java
abstract class Animal {
    abstract void makeSound();
}

class Dog extends Animal {
    void makeSound() {
        System.out.println("Bark");
    }
}

public class Test {
    public static void main(String[] args) {
        Animal animal = new Dog();
        animal.makeSound();
    }
}
```
A) Compilation error in Animal class  
B) Compilation error in Dog class  
C) Prints "Bark"  
D) Runtime error

**Answer: C) Prints "Bark"**

**Explanation**: This is a correct implementation. `Animal` is abstract with an abstract method `makeSound()`. `Dog` extends `Animal` and provides a concrete implementation of `makeSound()`. Through polymorphism, we can create a `Dog` object and reference it as an `Animal`, then call the overridden method.

---

### Question 5
Which statement is TRUE?
```java
abstract class Vehicle {
    static int count = 0;
    
    static void incrementCount() {
        count++;
    }
}
```
A) This code will not compile  
B) You cannot access static members without creating an instance  
C) You can call Vehicle.incrementCount() directly  
D) Static methods in abstract classes must also be abstract

**Answer: C) You can call Vehicle.incrementCount() directly**

**Explanation**: Abstract classes can have static methods and variables. Static members belong to the class itself, not to instances, so they can be accessed without creating an object. You can call `Vehicle.incrementCount()` even though `Vehicle` is abstract and cannot be instantiated.

---

### Question 6
What is the result of compiling this code?
```java
abstract class Parent {
    final abstract void method();
}
```
A) Compiles successfully  
B) Error: abstract methods cannot be final  
C) Error: abstract classes cannot have final methods  
D) Compiles with a warning

**Answer: B) Error: abstract methods cannot be final**

**Explanation**: Abstract methods must be overridden by subclasses, while final methods cannot be overridden. These concepts are contradictory. An abstract method cannot be final. Note that abstract classes CAN have final methods, but those must be concrete (have implementation), not abstract.

---

### Question 7
What is the output?
```java
abstract class Animal {
    abstract void makeSound();
    
    void breathe() {
        System.out.print("Breathing ");
    }
}

class Dog extends Animal {
    void makeSound() {
        System.out.print("Bark ");
    }
}

public class Test {
    public static void main(String[] args) {
        Dog dog = new Dog();
        dog.breathe();
        dog.makeSound();
    }
}
```
A) Bark Breathing  
B) Breathing Bark  
C) Compilation error  
D) Runtime error

**Answer: B) Breathing Bark**

**Explanation**: The `Dog` class inherits the concrete `breathe()` method from `Animal` and implements the abstract `makeSound()` method. When we call `dog.breathe()`, it prints "Breathing ", followed by `dog.makeSound()` printing "Bark ". Abstract classes can have both abstract and concrete methods.

---

### Question 8
Which is a valid reason to use an abstract class?
A) To create multiple instances of the abstract class  
B) To provide common code for related subclasses  
C) To avoid using inheritance  
D) To make all methods private

**Answer: B) To provide common code for related subclasses**

**Explanation**: Abstract classes are designed to provide common functionality and structure for related subclasses. They allow code reuse through inheritance while forcing subclasses to implement specific methods. Option A is wrong (cannot instantiate abstract classes), Option C is wrong (abstract classes are about using inheritance), and Option D is wrong (abstract methods cannot be private).

---

### Question 9
What happens when you compile this code?
```java
abstract class A {
    abstract void method1();
    abstract void method2();
}

class B extends A {
    void method1() {
        System.out.println("Method1");
    }
}
```
A) Compiles successfully  
B) Compilation error: B must implement method2  
C) Compilation error: B must be abstract  
D) Both B and C are correct

**Answer: D) Both B and C are correct**

**Explanation**: Class `B` extends abstract class `A` but only implements `method1()`, not `method2()`. There are two ways to fix this: either implement `method2()` in `B` (option B), or declare `B` as abstract (option C). Since `B` is declared as a concrete class but doesn't implement all abstract methods, it causes a compilation error.

---

### Question 10
What is the output?
```java
abstract class Calculator {
    abstract int calculate(int a, int b);
    
    final int square(int n) {
        return n * n;
    }
}

class Adder extends Calculator {
    int calculate(int a, int b) {
        return a + b;
    }
    
    int square(int n) {  // Line X
        return n * n * n;
    }
}
```
A) Compiles and runs successfully  
B) Compilation error at Line X  
C) Runtime error  
D) Compilation error in Calculator class

**Answer: B) Compilation error at Line X**

**Explanation**: The `square()` method in `Calculator` is declared as `final`, which means it cannot be overridden. When `Adder` tries to override it at Line X, a compilation error occurs. Abstract classes can have final concrete methods, and those cannot be overridden by subclasses.

---

### Question 11
Which statement about this code is TRUE?
```java
abstract class Animal {
    private String name;
    
    Animal(String name) {
        this.name = name;
    }
    
    String getName() {
        return name;
    }
}

class Dog extends Animal {
    Dog(String name) {
        super(name);
    }
}
```
A) Compilation error: abstract classes cannot have constructors  
B) Compilation error: abstract classes cannot have instance variables  
C) Compiles successfully  
D) Runtime error when creating a Dog object

**Answer: C) Compiles successfully**

**Explanation**: Abstract classes can have constructors, instance variables, and concrete methods. When a `Dog` object is created, its constructor calls `super(name)` to invoke the `Animal` constructor. This is a perfectly valid use of an abstract class to share common fields and initialization logic.

---

### Question 12
What is required for this code to compile?
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
    
    double area() {
        return Math.PI * radius * radius;
    }
}
```
A) Nothing, it compiles as is  
B) Implement perimeter() in Circle  
C) Make Circle abstract  
D) Either B or C

**Answer: D) Either B or C**

**Explanation**: `Circle` extends `Shape` but only implements `area()`, not `perimeter()`. To compile, you must either implement all abstract methods (option B) or declare `Circle` as abstract (option C). A concrete class extending an abstract class must implement all abstract methods.

---

### Question 13
What is the output?
```java
abstract class Vehicle {
    void start() {
        System.out.print("Starting ");
    }
}

class Car extends Vehicle {
    void start() {
        super.start();
        System.out.print("Car ");
    }
}

public class Test {
    public static void main(String[] args) {
        Vehicle v = new Car();
        v.start();
    }
}
```
A) Car  
B) Starting  
C) Starting Car  
D) Compilation error

**Answer: C) Starting Car**

**Explanation**: The `start()` method in `Vehicle` is not abstract—it's a regular concrete method. `Car` overrides it and calls `super.start()` first, which prints "Starting ", then prints "Car ". This demonstrates that abstract classes can have concrete methods that can be overridden.

---

### Question 14
Which statement is FALSE?
A) An abstract class can extend another abstract class  
B) An abstract class can implement an interface without implementing all interface methods  
C) An abstract class must have at least one abstract method  
D) An abstract class can have a main() method

**Answer: C) An abstract class must have at least one abstract method**

**Explanation**: An abstract class does NOT need to have any abstract methods. A class can be declared abstract just to prevent instantiation, even if all its methods are concrete. All other statements are true: abstract classes can extend other abstract classes, can implement interfaces partially, and can have a main() method.

---

### Question 15
What happens when you compile this code?
```java
abstract class A {
    abstract void method();
}

abstract class B extends A {
    // Does not implement method()
}

class C extends B {
    void method() {
        System.out.println("Implemented");
    }
}
```
A) Compilation error in class B  
B) Compilation error in class C  
C) Compiles successfully  
D) Runtime error

**Answer: C) Compiles successfully**

**Explanation**: This demonstrates multiple levels of abstraction. Abstract class `B` extends abstract class `A` but doesn't implement the abstract `method()`—this is allowed because `B` is also abstract. The concrete class `C` extends `B` and must implement all inherited abstract methods, which it does. This is valid.

---

### Question 16
What is the purpose of the Template Method pattern using abstract classes?
```java
abstract class DataProcessor {
    final void process() {
        readData();
        processData();
        writeData();
    }
    
    abstract void processData();
    
    void readData() { /* default implementation */ }
    void writeData() { /* default implementation */ }
}
```
A) To allow multiple inheritance  
B) To define algorithm skeleton with customizable steps  
C) To prevent method overriding  
D) To avoid using interfaces

**Answer: B) To define algorithm skeleton with customizable steps**

**Explanation**: The Template Method pattern defines the skeleton of an algorithm in a method (here, `process()`), deferring some steps to subclasses. The `process()` method is final (cannot be changed), but `processData()` is abstract and must be implemented by subclasses, allowing customization while maintaining the overall algorithm structure.

---

### Question 17
What is the result?
```java
abstract class Animal {
    static void info() {
        System.out.print("Animal ");
    }
    
    abstract void makeSound();
}

class Dog extends Animal {
    static void info() {
        System.out.print("Dog ");
    }
    
    void makeSound() {
        System.out.print("Bark");
    }
}

public class Test {
    public static void main(String[] args) {
        Animal animal = new Dog();
        animal.info();
        animal.makeSound();
    }
}
```
A) Animal Bark  
B) Dog Bark  
C) Compilation error  
D) Animal Dog Bark

**Answer: A) Animal Bark**

**Explanation**: Static methods are not polymorphic. When calling `animal.info()`, the method is resolved based on the reference type (`Animal`), not the object type (`Dog`). This is static binding. Then `makeSound()` is called polymorphically based on the actual object type, printing "Bark". Static methods are class members, not instance members.

---

### Question 18
Which code demonstrates a valid use of abstract classes?
A)
```java
abstract class A {
    A() { }
    abstract void method();
}
class B extends A {
    void method() { }
}
```
B)
```java
abstract class A {
    abstract void method() { }
}
```
C)
```java
abstract class A {
    static abstract void method();
}
```
D)
```java
abstract class A {
    private abstract void method();
}
```

**Answer: A)**

**Explanation**: Option A is correct—abstract class with constructor and abstract method, extended by concrete class that implements the abstract method. Option B is invalid (abstract methods cannot have a body), Option C is invalid (abstract methods cannot be static), and Option D is invalid (abstract methods cannot be private).

---

### Question 19
What is true about this code?
```java
abstract class Shape {
    protected String color;
    
    Shape(String color) {
        this.color = color;
    }
    
    abstract double area();
    
    void displayColor() {
        System.out.println("Color: " + color);
    }
}
```
A) Shape cannot have instance variables  
B) Shape cannot have a constructor  
C) Shape can be used as a type for polymorphism  
D) Shape must have only abstract methods

**Answer: C) Shape can be used as a type for polymorphism**

**Explanation**: Although `Shape` cannot be instantiated, it can be used as a reference type for polymorphism. You can declare `Shape shape = new Circle("Red")` where `Circle` extends `Shape`. Abstract classes can have instance variables (A is false), constructors (B is false), and concrete methods (D is false).

---

### Question 20
What happens when you run this code?
```java
abstract class Calculator {
    int add(int a, int b) {
        return a + b;
    }
}

public class Test {
    public static void main(String[] args) {
        Calculator calc = new Calculator();
        System.out.println(calc.add(5, 3));
    }
}
```
A) Prints 8  
B) Prints 0  
C) Compilation error  
D) Runtime error

**Answer: C) Compilation error**

**Explanation**: Even though `Calculator` has no abstract methods, it is declared as abstract, which means it cannot be instantiated. The line `new Calculator()` causes a compilation error. To use this class, you must create a concrete subclass and instantiate that instead.

---

## Answer Summary
1. D  2. C  3. C  4. C  5. C  
6. B  7. B  8. B  9. D  10. B  
11. C  12. D  13. C  14. C  15. C  
16. B  17. A  18. A  19. C  20. C
