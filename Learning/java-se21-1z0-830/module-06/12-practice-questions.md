# Module 6.1: Inheritance - Practice Questions

## 📝 Practice Exam (20 Questions)

**Time Limit:** 30 minutes  
**Passing Score:** 16/20 (80%)

---

### Question 1
What is the output?

```java
class Parent {
    void display() {
        System.out.println("Parent");
    }
}

class Child extends Parent {
    void display() {
        System.out.println("Child");
    }
}

public class Test {
    public static void main(String[] args) {
        Parent obj = new Child();
        obj.display();
    }
}
```

A) Parent  
B) Child  
C) Compilation error  
D) Runtime exception  

**Answer:** B

**Explanation:**
Polymorphism - the actual object type (Child) determines which method is called at runtime. Output: Child

---

### Question 2
Which keyword is used to inherit a class?

A) implements  
B) inherits  
C) extends  
D) super  

**Answer:** C

**Explanation:**
The `extends` keyword is used for class inheritance. `implements` is used for interfaces.

---

### Question 3
What happens with this code?

```java
class Parent {
    Parent(int x) {
        System.out.println(x);
    }
}

class Child extends Parent {
    Child() {
        System.out.println("Child");
    }
}
```

A) Prints: 0 Child  
B) Compiles successfully  
C) Compilation error  
D) Runtime exception  

**Answer:** C

**Explanation:**
Parent has no no-arg constructor. Child's constructor must explicitly call `super(value)` as the first statement. Compilation error.

---

### Question 4
What is the output?

```java
class Parent {
    Parent() {
        System.out.println("Parent");
    }
}

class Child extends Parent {
    Child() {
        System.out.println("Child");
    }
}

public class Test {
    public static void main(String[] args) {
        new Child();
    }
}
```

A) Child  
B) Parent  
C) Parent Child  
D) Child Parent  

**Answer:** C

**Explanation:**
Constructor chaining: parent constructor executes first (implicit `super()`), then child constructor. Output: Parent Child

---

### Question 5
Which statement about method overriding is TRUE?

A) Return type can be different  
B) Access modifier can be more restrictive  
C) Method signature must match  
D) Static methods can be overridden  

**Answer:** C

**Explanation:**
Method overriding requires the same method signature (name and parameters). Return type must be same or covariant, access cannot be more restrictive, and static methods are hidden, not overridden.

---

### Question 6
What is the output?

```java
class Parent {
    int value = 10;
}

class Child extends Parent {
    int value = 20;
    
    void display() {
        System.out.println(value);
        System.out.println(super.value);
    }
}

public class Test {
    public static void main(String[] args) {
        new Child().display();
    }
}
```

A) 10 10  
B) 20 20  
C) 20 10  
D) 10 20  

**Answer:** C

**Explanation:**
`value` refers to Child's field (20). `super.value` explicitly accesses Parent's field (10). Output: 20 10

---

### Question 7
How many classes can a Java class extend?

A) 0  
B) 1  
C) 2  
D) Unlimited  

**Answer:** B

**Explanation:**
Java supports single inheritance only. A class can extend exactly one parent class (or implicitly extends Object if no parent specified).

---

### Question 8
What is the purpose of the @Override annotation?

A) Mandatory for overriding  
B) Helps catch errors at compile-time  
C) Changes method behavior  
D) Makes methods final  

**Answer:** B

**Explanation:**
@Override is optional but recommended. It helps catch typos and signature mismatches at compile-time.

---

### Question 9
What happens with this code?

```java
final class Parent {
    void display() {
        System.out.println("Parent");
    }
}

class Child extends Parent {
    void display() {
        System.out.println("Child");
    }
}
```

A) Compiles successfully  
B) Compilation error - cannot extend final class  
C) Runtime exception  
D) Prints: Child  

**Answer:** B

**Explanation:**
Final classes cannot be extended. This is a compilation error.

---

### Question 10
What is the output?

```java
class Parent {
    void method() {
        System.out.println("Parent");
    }
}

class Child extends Parent {
    @Override
    void method() {
        super.method();
        System.out.println("Child");
    }
}

public class Test {
    public static void main(String[] args) {
        new Child().method();
    }
}
```

A) Parent  
B) Child  
C) Parent Child  
D) Compilation error  

**Answer:** C

**Explanation:**
Child's method calls parent's method using `super.method()`, then prints "Child". Output: Parent Child

---

### Question 11
Which method is inherited from the Object class?

A) toString()  
B) main()  
C) run()  
D) execute()  

**Answer:** A

**Explanation:**
`toString()`, `equals()`, `hashCode()`, and other methods are inherited from the Object class. All classes implicitly extend Object.

---

### Question 12
What is valid method overriding?

```java
class Parent {
    protected void method() { }
}
```

A) `private void method() { }` in child  
B) `public void method() { }` in child  
C) `void method(int x) { }` in child  
D) `final void method() { }` in parent  

**Answer:** B

**Explanation:**
Overriding can make access more permissive (protected -> public). Option A is more restrictive (error). Option C is overloading, not overriding. Option D in parent would prevent overriding.

---

### Question 13
What happens when super() is not the first statement?

```java
class Child extends Parent {
    Child() {
        System.out.println("Child");
        super();
    }
}
```

A) Compiles successfully  
B) Compilation error  
C) Runtime exception  
D) Prints: Child  

**Answer:** B

**Explanation:**
`super()` or `this()` must be the first statement in a constructor. This is a compilation error.

---

### Question 14
What is the output?

```java
class Parent {
    static void method() {
        System.out.println("Parent static");
    }
}

class Child extends Parent {
    static void method() {
        System.out.println("Child static");
    }
}

public class Test {
    public static void main(String[] args) {
        Parent obj = new Child();
        obj.method();
    }
}
```

A) Parent static  
B) Child static  
C) Compilation error  
D) Runtime exception  

**Answer:** A

**Explanation:**
Static methods are not overridden, they are hidden. The reference type (Parent) determines which method is called at compile-time. Output: Parent static

---

### Question 15
Which statement about final methods is TRUE?

A) Cannot be called  
B) Cannot be overridden  
C) Must be static  
D) Must be private  

**Answer:** B

**Explanation:**
Final methods cannot be overridden by subclasses. They can be called, can be instance or static, and can have any access modifier.

---

### Question 16
What is the output?

```java
class Parent {
    Parent() {
        System.out.println("A");
    }
}

class Child extends Parent {
    Child() {
        super();
        System.out.println("B");
    }
}

public class Test {
    public static void main(String[] args) {
        new Child();
    }
}
```

A) A  
B) B  
C) A B  
D) B A  

**Answer:** C

**Explanation:**
Explicit `super()` call executes parent constructor first, then child constructor. Output: A B

---

### Question 17
What is covariant return type?

A) Returning the same type  
B) Returning a subtype of the original return type  
C) Returning a supertype  
D) Not allowed in Java  

**Answer:** B

**Explanation:**
Covariant return type allows an overriding method to return a subtype of the return type declared in the parent method.

```java
class Parent {
    Number getValue() { return 10; }
}
class Child extends Parent {
    @Override
    Integer getValue() { return 20; }  // Integer is subtype of Number
}
```

---

### Question 18
What happens with this code?

```java
class Parent {
    final void display() {
        System.out.println("Parent");
    }
}

class Child extends Parent {
    @Override
    void display() {
        System.out.println("Child");
    }
}
```

A) Compiles successfully  
B) Compilation error - cannot override final method  
C) Runtime exception  
D) Prints: Child  

**Answer:** B

**Explanation:**
Final methods cannot be overridden. This is a compilation error.

---

### Question 19
All Java classes implicitly extend which class?

A) Class  
B) Object  
C) Parent  
D) Super  

**Answer:** B

**Explanation:**
All classes implicitly extend the Object class if no explicit parent is specified. Object is the root of the class hierarchy.

---

### Question 20
What is the output?

```java
class Parent {
    Parent(int x) {
        this(x, 0);
        System.out.println("A");
    }
    
    Parent(int x, int y) {
        System.out.println("B");
    }
}

class Child extends Parent {
    Child() {
        super(10);
    }
}

public class Test {
    public static void main(String[] args) {
        new Child();
    }
}
```

A) A  
B) B  
C) B A  
D) A B  

**Answer:** C

**Explanation:**
Child calls `super(10)` -> Parent(int) -> `this(x, 0)` -> Parent(int, int) prints "B", then Parent(int) prints "A". Output: B A

---

## 📊 Scoring Guide

**Score Interpretation:**
- **18-20 (90-100%)**: Excellent! You have mastered inheritance.
- **16-17 (80-89%)**: Good! Review the questions you missed.
- **14-15 (70-79%)**: Fair. Revisit the theory and practice more.
- **Below 14 (< 70%)**: Need more study. Review the theory document carefully.

---

## 🎯 Common Mistakes to Avoid

1. **Missing super() call** when parent has no no-arg constructor
2. **super() position** - must be first statement in constructor
3. **Overriding vs hiding** - static methods are hidden, not overridden
4. **Final methods** - cannot be overridden
5. **Final classes** - cannot be extended
6. **Access modifiers** - cannot make overriding method more restrictive
7. **Constructor chaining** - parent constructor runs before child

---

## Next Steps

✅ **Scored 16+?** Move to [Polymorphism and Casting](13-polymorphism-casting.md)

⚠️ **Scored below 16?** Review [Inheritance Theory](12-inheritance.md) and retake this quiz.

---

**Good luck!** ☕
