# Module 5.1: Classes and Objects - Practice Questions

## 📝 Practice Exam (20 Questions)

**Time Limit:** 30 minutes  
**Passing Score:** 16/20 (80%)

---

### Question 1
What is the output?

```java
public class Test {
    static int x = 10;
    
    public static void main(String[] args) {
        Test t1 = new Test();
        Test t2 = new Test();
        t1.x = 20;
        System.out.println(t2.x);
    }
}
```

A) 10  
B) 20  
C) Compilation error  
D) Runtime exception  

**Answer:** B

**Explanation:**
`x` is a static variable, shared by all instances of the class. When `t1.x = 20` executes, it modifies the static variable. Both `t1.x` and `t2.x` refer to the same static variable, so `t2.x` is 20.

---

### Question 2
Which statement about constructors is FALSE?

A) Constructor name must match the class name  
B) Constructors can have return type void  
C) Constructors are called when an object is created  
D) Constructors can be overloaded  

**Answer:** B

**Explanation:**
Constructors CANNOT have a return type, not even void. If you specify a return type, it becomes a regular method, not a constructor.

---

### Question 3
What is the output?

```java
public class Person {
    String name;
    
    public Person(String name) {
        name = name;
    }
    
    public static void main(String[] args) {
        Person p = new Person("Alice");
        System.out.println(p.name);
    }
}
```

A) Alice  
B) null  
C) Compilation error  
D) Runtime exception  

**Answer:** B

**Explanation:**
Missing `this.` - the parameter `name` shadows the instance field `name`. The assignment `name = name` assigns the parameter to itself, not to the field. The field remains null.

---

### Question 4
What happens with this code?

```java
public class Test {
    int value;
    
    static void modify(int value) {
        value = 10;
    }
    
    public static void main(String[] args) {
        // modify(value);  // Line X
    }
}
```

A) Compiles and runs successfully  
B) Compilation error at Line X  
C) Runtime exception  
D) value is set to 10  

**Answer:** B

**Explanation:**
Static method `modify` cannot access instance variable `value` without an object reference. This is a compilation error.

---

### Question 5
What is the default value of an uninitialized instance variable of type `int`?

A) 0  
B) null  
C) undefined  
D) Compilation error  

**Answer:** A

**Explanation:**
Instance variables are automatically initialized to default values. For int, the default is 0. For objects, it's null. For boolean, it's false.

---

### Question 6
What is the output?

```java
public class Counter {
    static int count = 0;
    
    public Counter() {
        count++;
    }
    
    public static void main(String[] args) {
        new Counter();
        new Counter();
        new Counter();
        System.out.println(Counter.count);
    }
}
```

A) 0  
B) 1  
C) 3  
D) Compilation error  

**Answer:** C

**Explanation:**
Each time `new Counter()` is called, the constructor increments the static variable `count`. After 3 objects are created, count is 3.

---

### Question 7
Which access modifier makes a field accessible only within the same class?

A) public  
B) protected  
C) private  
D) default  

**Answer:** C

**Explanation:**
`private` restricts access to only the same class. It's the most restrictive access modifier.

---

### Question 8
What is the output?

```java
public class Test {
    int x = 10;
    
    void method() {
        int x = 20;
        System.out.println(x);
        System.out.println(this.x);
    }
    
    public static void main(String[] args) {
        new Test().method();
    }
}
```

A) 10 10  
B) 20 20  
C) 20 10  
D) Compilation error  

**Answer:** C

**Explanation:**
Local variable `x` (20) shadows the instance variable. `x` refers to local variable (20), while `this.x` refers to instance variable (10).

---

### Question 9
What happens when no constructor is defined in a class?

A) Compilation error  
B) Java provides a default no-arg constructor  
C) The class cannot be instantiated  
D) Runtime exception  

**Answer:** B

**Explanation:**
If no constructor is explicitly defined, Java automatically provides a default no-argument constructor that does nothing.

---

### Question 10
What is the output?

```java
public class Box {
    static {
        System.out.print("A");
    }
    
    {
        System.out.print("B");
    }
    
    public Box() {
        System.out.print("C");
    }
    
    public static void main(String[] args) {
        new Box();
        new Box();
    }
}
```

A) ABCABC  
B) ABC ABC  
C) ABCBC  
D) BCBC  

**Answer:** C

**Explanation:**
Order: static block (once) → instance block → constructor (for each object).
- Static block runs once: A
- First object: B (instance), C (constructor)
- Second object: B (instance), C (constructor)
Output: ABCBC

---

### Question 11
Which statement about static methods is TRUE?

A) Can access instance variables directly  
B) Can use `this` keyword  
C) Can be called without creating an object  
D) Cannot be overloaded  

**Answer:** C

**Explanation:**
Static methods belong to the class and can be called using the class name without creating an object (e.g., `ClassName.methodName()`).

---

### Question 12
What is the output?

```java
public class Product {
    String name;
    
    public Product(String name) {
        this.name = name;
    }
    
    public static void main(String[] args) {
        Product p1 = new Product("Laptop");
        Product p2 = p1;
        p2.name = "Desktop";
        System.out.println(p1.name);
    }
}
```

A) Laptop  
B) Desktop  
C) null  
D) Compilation error  

**Answer:** B

**Explanation:**
`p2 = p1` makes both references point to the same object. Changing `p2.name` changes the object that both `p1` and `p2` reference. Output: Desktop

---

### Question 13
What happens with this code?

```java
public class Test {
    public Test() {
        System.out.println("Constructor 1");
    }
    
    public void Test() {
        System.out.println("Constructor 2");
    }
}
```

A) Compilation error - duplicate constructors  
B) Compiles successfully  
C) Runtime exception  
D) Constructor overloading  

**Answer:** B

**Explanation:**
The second "Test" has a return type (void), making it a regular method, not a constructor. Constructors cannot have return types. This code compiles but may be confusing.

---

### Question 14
What is the output?

```java
public class Calculator {
    int add(int a, int b) {
        return a + b;
    }
    
    static int subtract(int a, int b) {
        return a - b;
    }
    
    public static void main(String[] args) {
        // System.out.println(add(10, 5));  // Line X
        System.out.println(subtract(10, 5));
    }
}
```

A) 15 and 5  
B) 5  
C) Compilation error at Line X  
D) Runtime exception  

**Answer:** C (if Line X is uncommented)

**Explanation:**
The commented line would cause a compilation error. Static method `main` cannot directly call instance method `add` without an object. `subtract` is static, so it can be called directly. If Line X is uncommented, compilation fails.

---

### Question 15
Which keyword refers to the current object?

A) super  
B) this  
C) self  
D) current  

**Answer:** B

**Explanation:**
`this` is a reference to the current object. It's used to distinguish fields from parameters and to pass the current object.

---

### Question 16
What is the output?

```java
public class Account {
    private double balance;
    
    public Account(double balance) {
        this.balance = balance;
    }
    
    public static void main(String[] args) {
        Account acc = new Account(1000);
        System.out.println(acc.balance);
    }
}
```

A) 0.0  
B) 1000.0  
C) Compilation error  
D) Runtime exception  

**Answer:** B

**Explanation:**
Even though `balance` is private, it's accessible within the same class. The `main` method is in the same class, so it can access the private field. Output: 1000.0

---

### Question 17
What happens when you define a parameterized constructor but not a no-arg constructor?

A) Java provides default no-arg constructor  
B) No default constructor is provided  
C) Compilation error  
D) Runtime exception  

**Answer:** B

**Explanation:**
If you define any constructor, Java does NOT provide a default no-arg constructor. You must explicitly define it if needed.

---

### Question 18
What is the output?

```java
public class Test {
    int value;
    
    public Test() {
        this(10);
    }
    
    public Test(int value) {
        this.value = value;
    }
    
    public static void main(String[] args) {
        Test t = new Test();
        System.out.println(t.value);
    }
}
```

A) 0  
B) 10  
C) Compilation error  
D) Runtime exception  

**Answer:** B

**Explanation:**
Constructor chaining: `new Test()` calls the no-arg constructor, which calls `this(10)`, invoking the parameterized constructor with value 10. Output: 10

---

### Question 19
Which is NOT a valid access modifier in Java?

A) public  
B) private  
C) package  
D) protected  

**Answer:** C

**Explanation:**
Java has four access levels: public, protected, default (no modifier), and private. "package" is not a valid access modifier keyword.

---

### Question 20
What is the output?

```java
public class Rectangle {
    int width = 10;
    int height = 20;
    
    public Rectangle(int width, int height) {
        width = width;
        height = height;
    }
    
    public static void main(String[] args) {
        Rectangle r = new Rectangle(30, 40);
        System.out.println(r.width + " " + r.height);
    }
}
```

A) 30 40  
B) 10 20  
C) 0 0  
D) Compilation error  

**Answer:** B

**Explanation:**
Missing `this.` - parameters shadow instance fields. `width = width` assigns parameter to itself, not to the field. Fields retain their initialized values: 10 and 20.

---

## 📊 Scoring Guide

**Score Interpretation:**
- **18-20 (90-100%)**: Excellent! You have mastered classes and objects.
- **16-17 (80-89%)**: Good! Review the questions you missed.
- **14-15 (70-79%)**: Fair. Revisit the theory and practice more.
- **Below 14 (< 70%)**: Need more study. Review the theory document carefully.

---

## 🎯 Common Mistakes to Avoid

1. **Forgetting `this`** in constructors and methods
2. **Accessing instance from static** - static can't directly access instance members
3. **Constructor return types** - constructors have no return type
4. **Default constructor** - not provided if you define any constructor
5. **Static vs instance** - understand which belongs to class vs object
6. **Access modifiers** - know visibility rules
7. **Object references** - multiple references can point to same object

---

## Next Steps

✅ **Scored 16+?** Move to [Methods and Parameters](10-methods-parameters.md)

⚠️ **Scored below 16?** Review [Classes and Objects Theory](09-classes-objects.md) and retake this quiz.

---

**Good luck!** ☕
