# Module 6: Polymorphism and Type Casting - Practice Questions

## Practice Questions (20)

### Question 1
What is the output of the following code?
```java
class Animal {
    void makeSound() {
        System.out.println("Animal sound");
    }
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
A) Animal sound  
B) Bark  
C) Compilation error  
D) Runtime error

**Answer: B) Bark**

**Explanation**: This demonstrates runtime polymorphism. Although the reference type is `Animal`, the actual object is a `Dog`. Java uses dynamic method dispatch to determine which `makeSound()` method to call at runtime. Since the actual object is a `Dog`, the overridden method in `Dog` class is executed.

---

### Question 2
Which statement about upcasting is TRUE?
```java
Dog dog = new Dog();
Animal animal = dog;  // Line X
```
A) Line X requires an explicit cast  
B) Line X may throw a ClassCastException  
C) Line X is always safe and implicit  
D) Line X will cause a compilation error

**Answer: C) Line X is always safe and implicit**

**Explanation**: Upcasting (converting a subclass reference to a superclass reference) is always safe because every Dog IS-AN Animal. It doesn't require an explicit cast and will never throw a `ClassCastException`. The compiler allows this conversion implicitly.

---

### Question 3
What is the output?
```java
class Parent {
    void display() {
        System.out.print("Parent ");
    }
}

class Child extends Parent {
    void display() {
        System.out.print("Child ");
    }
    
    void show() {
        System.out.print("Show ");
    }
}

public class Test {
    public static void main(String[] args) {
        Parent p = new Child();
        p.display();
        p.show();
    }
}
```
A) Parent Show  
B) Child Show  
C) Parent  
D) Compilation error

**Answer: D) Compilation error**

**Explanation**: Although the actual object is a `Child`, the reference type is `Parent`. The `Parent` class doesn't have a `show()` method, so `p.show()` causes a compilation error. The reference type determines which methods can be called at compile time, even though the actual object type determines which method implementation runs at runtime.

---

### Question 4
What will happen when this code executes?
```java
Animal animal = new Cat();
Dog dog = (Dog) animal;
```
A) Compiles and runs successfully  
B) Compilation error  
C) Throws ClassCastException at runtime  
D) Throws NullPointerException

**Answer: C) Throws ClassCastException at runtime**

**Explanation**: The code compiles successfully because the compiler only checks if the cast is possible (Dog and Cat are both Animals). However, at runtime, Java checks the actual object type. Since the actual object is a Cat, it cannot be cast to a Dog, resulting in a `ClassCastException`.

---

### Question 5
Which statement about the `instanceof` operator is FALSE?
```java
String str = "Hello";
Object obj = null;
```
A) `str instanceof Object` returns true  
B) `obj instanceof String` returns false  
C) `null instanceof Object` returns false  
D) `obj instanceof Object` throws NullPointerException

**Answer: D) `obj instanceof Object` throws NullPointerException**

**Explanation**: The `instanceof` operator is null-safe. When used with a null reference, it simply returns false instead of throwing a `NullPointerException`. All other statements are true: String is an Object (A), null instanceof anything is false (B and C).

---

### Question 6
What is the output? (Java 16+)
```java
Object obj = "Hello";

if (obj instanceof String str) {
    System.out.print(str.length() + " ");
}
System.out.print(str.length());
```
A) 5 5  
B) Compilation error  
C) 5  
D) Runtime error

**Answer: B) Compilation error**

**Explanation**: This demonstrates pattern matching for instanceof. The pattern variable `str` is only in scope within the if block where the instanceof check succeeded. Outside the if block, `str` is not in scope, causing a compilation error on the second `str.length()` call.

---

### Question 7
Which code correctly uses downcasting?
```java
Animal animal = new Dog();
```
A) `Dog dog = animal;`  
B) `Dog dog = (Dog) animal;`  
C) `Dog dog = animal as Dog;`  
D) `Dog dog = animal.toDog();`

**Answer: B) `Dog dog = (Dog) animal;`**

**Explanation**: Downcasting requires an explicit cast using the cast operator `(Type)`. Option A would cause a compilation error because Animal cannot be automatically converted to Dog. Options C and D use incorrect syntax (Java doesn't have an `as` operator like C#, and there's no `toDog()` method).

---

### Question 8
What is the output?
```java
class Shape {
    String type = "Shape";
}

class Circle extends Shape {
    String type = "Circle";
}

public class Test {
    public static void main(String[] args) {
        Shape shape = new Circle();
        System.out.println(shape.type);
    }
}
```
A) Shape  
B) Circle  
C) Compilation error  
D) Runtime error

**Answer: A) Shape**

**Explanation**: Unlike methods, instance variables are not polymorphic. Variable access is determined by the reference type, not the object type. Since the reference type is `Shape`, `shape.type` accesses the `type` variable in the `Shape` class. This is called variable hiding (not overriding).

---

### Question 9
What happens with this code? (Java 16+)
```java
Object obj = Integer.valueOf(42);

if (obj instanceof String str || str.length() > 0) {
    System.out.println("String");
}
```
A) Prints "String"  
B) No output  
C) Compilation error  
D) Runtime error

**Answer: C) Compilation error**

**Explanation**: In a logical OR condition, the pattern variable `str` might not be initialized (if the instanceof check is false, the right side of OR might still be evaluated). Pattern variables can only be used in contexts where they are definitely assigned. Using `||` with pattern variables results in a compilation error because `str` might not be initialized when evaluating `str.length()`.

---

### Question 10
What is the result?
```java
interface Flyable {
    void fly();
}

class Bird implements Flyable {
    public void fly() {
        System.out.println("Bird flies");
    }
}

public class Test {
    public static void main(String[] args) {
        Object obj = new Bird();
        System.out.println(obj instanceof Flyable);
    }
}
```
A) true  
B) false  
C) Compilation error  
D) Runtime error

**Answer: A) true**

**Explanation**: The instanceof operator works with interfaces as well. Even though the reference type is `Object`, the actual object is a `Bird` instance, which implements `Flyable`. Therefore, `obj instanceof Flyable` returns true. The instanceof check is based on the actual object type, not the reference type.

---

### Question 11
What is printed?
```java
class Vehicle {
    void start() {
        System.out.print("Vehicle ");
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
A) Vehicle  
B) Car  
C) Vehicle Car  
D) Car Vehicle

**Answer: C) Vehicle Car**

**Explanation**: Even though the reference is `Vehicle`, polymorphism ensures that `Car`'s overridden `start()` method is called. Inside `Car.start()`, `super.start()` calls the parent class's method first (printing "Vehicle "), then the rest of `Car.start()` executes (printing "Car ").

---

### Question 12
Which statement is TRUE about this code?
```java
Animal[] animals = new Dog[5];
animals[0] = new Cat();  // Line X
```
A) Line X compiles and runs without error  
B) Line X causes a compilation error  
C) Line X throws ArrayStoreException at runtime  
D) Line X throws ClassCastException at runtime

**Answer: C) Line X throws ArrayStoreException at runtime**

**Explanation**: This demonstrates array covariance. The code compiles because `Animal[]` can reference a `Dog[]` (upcasting). However, at runtime, Java remembers that the array is actually a `Dog[]`. When you try to store a `Cat` in it, Java throws an `ArrayStoreException` because a Cat is not a Dog.

---

### Question 13
What is the output? (Java 16+)
```java
Object obj = "Test";

if (obj instanceof String str && str.length() > 2) {
    System.out.print("A");
}
if (!(obj instanceof Integer num)) {
    System.out.print("B");
}
```
A) A  
B) B  
C) AB  
D) Compilation error

**Answer: C) AB**

**Explanation**: In the first if statement, pattern matching succeeds (obj is a String) and the length is 4, so "A" is printed. In the second if statement, the condition is negated—obj is not an Integer, so the condition is true and "B" is printed. Note that `num` is not in scope inside the if block because the instanceof check is negated.

---

### Question 14
What happens when you run this code?
```java
class Parent { }
class Child extends Parent { }
class GrandChild extends Child { }

public class Test {
    public static void main(String[] args) {
        Parent p = new GrandChild();
        Child c = (Child) p;
        GrandChild gc = (GrandChild) c;
        System.out.println("Success");
    }
}
```
A) Prints "Success"  
B) Compilation error  
C) ClassCastException at second cast  
D) ClassCastException at third cast

**Answer: A) Prints "Success"**

**Explanation**: The actual object is a `GrandChild` instance. All the casts are valid because a GrandChild IS-A Child and IS-A Parent. Downcasting from Parent to Child and then to GrandChild is safe in this case because the actual object type supports these casts.

---

### Question 15
What is the output?
```java
class A {
    void method() {
        System.out.print("A");
    }
}

class B extends A {
    void method() {
        System.out.print("B");
    }
}

class C extends B {
    void method() {
        System.out.print("C");
    }
}

public class Test {
    public static void main(String[] args) {
        A a = new C();
        a.method();
        
        B b = (B) a;
        b.method();
    }
}
```
A) AB  
B) AC  
C) CC  
D) BC

**Answer: C) CC**

**Explanation**: The actual object is always a `C` instance. Due to polymorphism, calling `method()` through any reference (A or B) will execute the most specific overridden version, which is `C.method()`. The reference type doesn't change which method implementation runs—only the actual object type matters.

---

### Question 16
Which cast will cause a compilation error?
```java
class Animal { }
class Dog extends Animal { }
class Cat extends Animal { }
```
A) `Animal a = new Dog(); Dog d = (Dog) a;`  
B) `Animal a = new Cat(); Dog d = (Dog) a;`  
C) `Dog d = new Dog(); Animal a = (Animal) d;`  
D) `Dog d = new Dog(); Cat c = (Cat) d;`

**Answer: D) `Dog d = new Dog(); Cat c = (Cat) d;`**

**Explanation**: The compiler checks if a cast is theoretically possible based on the inheritance hierarchy. Dog and Cat are siblings (both extend Animal) but have no parent-child relationship. Therefore, casting directly from Dog to Cat is not possible, causing a compilation error. Options A, B, and C compile (though B would throw a runtime exception).

---

### Question 17
What is the output? (Java 16+)
```java
Object obj = 42;

if (obj instanceof Integer num) {
    System.out.print(num + 10);
}
```
A) 42  
B) 52  
C) 4210  
D) Compilation error

**Answer: B) 52**

**Explanation**: Pattern matching for instanceof automatically casts the object to the specified type. The pattern variable `num` is of type `Integer` (not `int`), but when used in the expression `num + 10`, auto-unboxing converts it to int, performs the addition (42 + 10 = 52), and prints the result.

---

### Question 18
What is true about this code?
```java
List<String> list = new ArrayList<>();
Object obj = list;
List<Integer> intList = (List<Integer>) obj;  // Line X
```
A) Line X is type-safe  
B) Line X causes a compilation error  
C) Line X compiles but may cause issues later  
D) Line X throws ClassCastException

**Answer: C) Line X compiles but may cause issues later**

**Explanation**: Due to type erasure, generic type information is not available at runtime. The cast compiles successfully (with an unchecked warning) because at runtime, both `List<String>` and `List<Integer>` are just `List`. However, if you try to add an Integer to intList or retrieve elements expecting Integers, you'll get a `ClassCastException` later.

---

### Question 19
What is printed?
```java
class Animal {
    static void info() {
        System.out.print("Animal");
    }
}

class Dog extends Animal {
    static void info() {
        System.out.print("Dog");
    }
}

public class Test {
    public static void main(String[] args) {
        Animal animal = new Dog();
        animal.info();
    }
}
```
A) Animal  
B) Dog  
C) Compilation error  
D) Runtime error

**Answer: A) Animal**

**Explanation**: Static methods are not polymorphic. They are resolved at compile time based on the reference type, not the object type. This is called static binding. Since the reference type is `Animal`, the `Animal.info()` method is called. This is different from instance methods, which use dynamic binding.

---

### Question 20
What happens with this code? (Java 16+)
```java
Object obj = null;

if (obj instanceof String str) {
    System.out.println(str.length());
}
System.out.println("Done");
```
A) NullPointerException  
B) Compilation error  
C) Prints "Done"  
D) No output

**Answer: C) Prints "Done"**

**Explanation**: The instanceof operator returns false when the left operand is null, regardless of the type being checked. Therefore, the if condition is false, the block doesn't execute, and the program continues to print "Done". Pattern matching for instanceof is null-safe, making this a safe way to check and cast in one operation.

---

## Answer Summary
1. B  2. C  3. D  4. C  5. D  
6. B  7. B  8. A  9. C  10. A  
11. C  12. C  13. C  14. A  15. C  
16. D  17. B  18. C  19. A  20. C
