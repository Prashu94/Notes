# Module 5.3: Varargs and Nested Classes - Practice Questions

## 📝 Practice Exam (20 Questions)

**Time Limit:** 30 minutes  
**Passing Score:** 16/20 (80%)

---

### Question 1
What is the output?

```java
public class Test {
    static void print(int... numbers) {
        System.out.println(numbers.length);
    }
    
    public static void main(String[] args) {
        print();
        print(1, 2, 3);
    }
}
```

A) 0 3  
B) 3 0  
C) Compilation error  
D) Runtime exception  

**Answer:** A

**Explanation:**
Varargs accepts zero or more arguments. First call has 0 arguments (length 0), second call has 3 arguments (length 3). Output: 0 and 3 on separate lines.

---

### Question 2
Which statement about varargs is FALSE?

A) Varargs must be the last parameter  
B) A method can have multiple varargs parameters  
C) Varargs is treated as an array  
D) Varargs can accept zero arguments  

**Answer:** B

**Explanation:**
A method can have only ONE varargs parameter, and it must be the last parameter in the parameter list.

---

### Question 3
How do you create an instance of a static nested class?

```java
public class Outer {
    static class Nested { }
}
```

A) `new Outer().new Nested()`  
B) `new Outer.Nested()`  
C) `new Nested()`  
D) `Outer.new Nested()`  

**Answer:** B

**Explanation:**
Static nested classes are instantiated using `new Outer.Nested()`. They don't require an outer instance.

---

### Question 4
What is the output?

```java
public class Outer {
    private int x = 10;
    
    class Inner {
        private int x = 20;
        
        void print() {
            System.out.println(x);
            System.out.println(Outer.this.x);
        }
    }
    
    public static void main(String[] args) {
        new Outer().new Inner().print();
    }
}
```

A) 10 10  
B) 20 20  
C) 20 10  
D) Compilation error  

**Answer:** C

**Explanation:**
`x` refers to Inner's x (20). `Outer.this.x` explicitly references Outer's x (10). Output: 20 and 10.

---

### Question 5
What happens with this code?

```java
public class Test {
    static class Nested {
        int value = 10;
    }
    
    public static void main(String[] args) {
        Nested n = new Nested();
        System.out.println(n.value);
    }
}
```

A) Prints: 10  
B) Compilation error  
C) Runtime exception  
D) Prints: 0  

**Answer:** A

**Explanation:**
Static nested classes can be instantiated without an outer instance. The code compiles and prints 10.

---

### Question 6
Which nested class type requires an outer class instance to be created?

A) Static nested class  
B) Inner class  
C) Both  
D) Neither  

**Answer:** B

**Explanation:**
Inner classes (non-static nested classes) require an instance of the outer class. Static nested classes do not.

---

### Question 7
What is the output?

```java
public class Test {
    static void method(String... args) {
        System.out.print("Varargs ");
    }
    
    static void method(String arg) {
        System.out.print("Single ");
    }
    
    public static void main(String[] args) {
        method("test");
    }
}
```

A) Varargs  
B) Single  
C) Compilation error  
D) Runtime exception  

**Answer:** B

**Explanation:**
When both methods match, the more specific method (single parameter) is chosen over varargs. Output: Single

---

### Question 8
What can an inner class access from the outer class?

A) Only public members  
B) Only static members  
C) All members (including private)  
D) Only protected members  

**Answer:** C

**Explanation:**
Inner classes have access to ALL members of the outer class, including private members.

---

### Question 9
What happens with this code?

```java
public class Outer {
    class Inner { }
    
    public static void main(String[] args) {
        Inner inner = new Inner();
    }
}
```

A) Compiles successfully  
B) Compilation error - need outer instance  
C) Runtime exception  
D) Creates Inner instance  

**Answer:** B

**Explanation:**
Inner classes require an outer instance. In static context (main), you need: `new Outer().new Inner()`. Compilation error.

---

### Question 10
What is valid syntax for varargs?

A) `void method(int... a, int... b)`  
B) `void method(int... a, int b)`  
C) `void method(int a, int... b)`  
D) `void method(...int a)`  

**Answer:** C

**Explanation:**
Varargs must be the last parameter and a method can have only one varargs. Option C is the only valid syntax.

---

### Question 11
What is the output?

```java
public class Test {
    public static void main(String[] args) {
        int x = 10;
        
        class Local {
            void print() {
                System.out.println(x);
            }
        }
        
        Local local = new Local();
        local.print();
    }
}
```

A) 10  
B) 0  
C) Compilation error  
D) Runtime exception  

**Answer:** A

**Explanation:**
Local classes can access effectively final local variables. `x` is effectively final (not modified), so it's accessible. Output: 10

---

### Question 12
Which statement about anonymous classes is TRUE?

A) They can have constructors  
B) They can extend multiple classes  
C) They can implement an interface or extend a class  
D) They must be static  

**Answer:** C

**Explanation:**
Anonymous classes can implement one interface OR extend one class (not both). They cannot have explicit constructors or extend multiple classes.

---

### Question 13
What happens when you pass null to a varargs method?

```java
public static void process(String... args) {
    System.out.println(args.length);
}

process(null);
```

A) Prints: 0  
B) Prints: 1  
C) NullPointerException  
D) Compilation error  

**Answer:** C

**Explanation:**
Passing `null` to varargs treats it as a null array reference, not an empty array. Accessing `args.length` throws NullPointerException.

---

### Question 14
What is required to create an inner class instance?

```java
public class Outer {
    class Inner { }
}
```

A) `new Inner()`  
B) `new Outer.Inner()`  
C) `new Outer().new Inner()`  
D) `Outer.new Inner()`  

**Answer:** C

**Explanation:**
Inner classes require an outer instance. Syntax: `outerInstance.new Inner()` or `new Outer().new Inner()`.

---

### Question 15
What is the output?

```java
public class Test {
    static int sum(int... numbers) {
        int total = 0;
        for (int num : numbers) {
            total += num;
        }
        return total;
    }
    
    public static void main(String[] args) {
        System.out.println(sum(1, 2, 3, 4, 5));
    }
}
```

A) 0  
B) 15  
C) 5  
D) Compilation error  

**Answer:** B

**Explanation:**
Varargs method accepts 5 arguments and sums them: 1 + 2 + 3 + 4 + 5 = 15.

---

### Question 16
Which nested class can access outer class's static members only?

A) Inner class  
B) Static nested class  
C) Local class  
D) Anonymous class  

**Answer:** B

**Explanation:**
Static nested classes can only access static members of the outer class directly. They cannot access instance members without an outer instance.

---

### Question 17
What is the output?

```java
interface Printer {
    void print(String message);
}

public class Test {
    public static void main(String[] args) {
        Printer printer = new Printer() {
            public void print(String message) {
                System.out.println("Message: " + message);
            }
        };
        printer.print("Hello");
    }
}
```

A) Message: Hello  
B) Hello  
C) Compilation error  
D) Runtime exception  

**Answer:** A

**Explanation:**
Anonymous class implements the Printer interface. The print method outputs "Message: Hello".

---

### Question 18
What happens with this code?

```java
public void method() {
    int x = 10;
    
    class Local {
        void modify() {
            x = 20;  // Line X
        }
    }
}
```

A) Compiles successfully  
B) Compilation error at Line X  
C) Runtime exception  
D) x becomes 20  

**Answer:** B

**Explanation:**
Local classes can only access effectively final local variables. Modifying `x` makes it not effectively final, causing a compilation error.

---

### Question 19
Which is a valid use of varargs?

A) `void method(int... a, String s)`  
B) `void method(String s, int... a)`  
C) `void method(int... a, int... b)`  
D) `void method(...int a, String s)`  

**Answer:** B

**Explanation:**
Varargs must be the last parameter. Only option B has varargs in the correct position.

---

### Question 20
What is the output?

```java
public class Outer {
    static int value = 10;
    
    static class Nested {
        void print() {
            System.out.println(value);
        }
    }
    
    public static void main(String[] args) {
        new Nested().print();
    }
}
```

A) 10  
B) 0  
C) Compilation error  
D) Runtime exception  

**Answer:** A

**Explanation:**
Static nested classes can access static members of the outer class. Prints: 10

---

## 📊 Scoring Guide

**Score Interpretation:**
- **18-20 (90-100%)**: Excellent! You have mastered varargs and nested classes.
- **16-17 (80-89%)**: Good! Review the questions you missed.
- **14-15 (70-79%)**: Fair. Revisit the theory and practice more.
- **Below 14 (< 70%)**: Need more study. Review the theory document carefully.

---

## 🎯 Common Mistakes to Avoid

1. **Varargs position** - must be last parameter
2. **Multiple varargs** - only one per method
3. **Inner class instantiation** - requires outer instance
4. **Static nested class** - doesn't require outer instance
5. **Local variable access** - must be effectively final
6. **Anonymous class constructors** - cannot have explicit constructors
7. **Null with varargs** - treats as null array, not empty

---

## Module 5 Complete! 🎉

You've completed the OOP Basics module covering:
- ✅ Classes and objects
- ✅ Constructors and initialization
- ✅ Methods and parameters
- ✅ Variable arguments (varargs)
- ✅ Nested classes (static, inner, local, anonymous)

**Total Practice Questions:** 60/60 ✓

---

## Next Steps

✅ **Scored 16+ on all quizzes?** Move to [Module 6: OOP Advanced](../module-06/12-inheritance.md)

⚠️ **Scored below 16?** Review the theory documents and retake the quizzes.

---

**Good luck!** ☕
