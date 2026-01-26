# Module 5.2: Methods and Parameters - Practice Questions

## 📝 Practice Exam (20 Questions)

**Time Limit:** 30 minutes  
**Passing Score:** 16/20 (80%)

---

### Question 1
What is the output?

```java
public class Test {
    public static void main(String[] args) {
        int x = 10;
        modify(x);
        System.out.println(x);
    }
    
    static void modify(int num) {
        num = 20;
    }
}
```

A) 10  
B) 20  
C) Compilation error  
D) Runtime exception  

**Answer:** A

**Explanation:**
Java is pass by value. The `modify` method receives a copy of `x`. Changing `num` doesn't affect `x`. Output: 10

---

### Question 2
Which of the following is valid method overloading?

```java
public int calculate(int a, int b) { return a + b; }
```

A) `public double calculate(int a, int b) { return a + b; }`  
B) `public int calculate(int x, int y) { return x + y; }`  
C) `public int calculate(double a, double b) { return (int)(a + b); }`  
D) `public void calculate(int a, int b) { }`  

**Answer:** C

**Explanation:**
Method overloading requires different parameter lists (type, count, or order). Option C changes parameter types from int to double, which is valid overloading. Option A only changes return type (invalid). Option B only changes parameter names (invalid).

---

### Question 3
What is the output?

```java
public class Test {
    public static void main(String[] args) {
        String str = "Hello";
        change(str);
        System.out.println(str);
    }
    
    static void change(String s) {
        s = "World";
    }
}
```

A) Hello  
B) World  
C) HelloWorld  
D) Compilation error  

**Answer:** A

**Explanation:**
Strings are immutable. The `change` method reassigns the local reference `s`, but doesn't affect the original `str` reference. Output: Hello

---

### Question 4
What happens with this code?

```java
public int getValue() {
    if (true) {
        return 10;
    }
    System.out.println("Done");
}
```

A) Returns 10  
B) Prints "Done" then returns 10  
C) Compilation error - unreachable code  
D) Runtime exception  

**Answer:** C

**Explanation:**
The `println` statement is unreachable because `return 10` always executes. This is a compilation error.

---

### Question 5
What is the output?

```java
public class Test {
    static int count = 0;
    
    static void increment() {
        count++;
    }
    
    public static void main(String[] args) {
        increment();
        increment();
        System.out.println(count);
    }
}
```

A) 0  
B) 1  
C) 2  
D) Compilation error  

**Answer:** C

**Explanation:**
Static method `increment` modifies the static variable `count`. Called twice, count becomes 2.

---

### Question 6
Which statement about method return types is TRUE?

A) void methods must have a return statement  
B) Non-void methods must return a value  
C) Return type can be omitted  
D) Methods can return multiple values  

**Answer:** B

**Explanation:**
Non-void methods must return a value of the declared type. Void methods don't need a return statement (or can have `return;` with no value).

---

### Question 7
What is the output?

```java
public class Test {
    public static void main(String[] args) {
        int[] arr = {1, 2, 3};
        modify(arr);
        System.out.println(arr[0]);
    }
    
    static void modify(int[] array) {
        array[0] = 100;
    }
}
```

A) 1  
B) 100  
C) 0  
D) Compilation error  

**Answer:** B

**Explanation:**
Arrays are objects. The reference value is passed, and the method modifies the actual array. arr[0] becomes 100.

---

### Question 8
How many parameters does this method accept?

```java
public void process(int a, String b, double... values) {
    // method body
}
```

A) 2  
B) 3  
C) Variable (at least 2)  
D) Compilation error  

**Answer:** C

**Explanation:**
Varargs (`double... values`) accepts zero or more arguments. This method requires at least 2 arguments (int and String), and can accept more doubles.

---

### Question 9
What is the output?

```java
public class Test {
    int value = 10;
    
    void method(int value) {
        System.out.println(value);
        System.out.println(this.value);
    }
    
    public static void main(String[] args) {
        new Test().method(20);
    }
}
```

A) 20 20  
B) 10 10  
C) 20 10  
D) Compilation error  

**Answer:** C

**Explanation:**
Parameter `value` (20) shadows instance variable. `value` prints parameter (20), `this.value` prints instance variable (10).

---

### Question 10
Which is a valid method signature?

A) `public int calculate(int a, int a) { }`  
B) `public void process() { return 10; }`  
C) `public String getName() { return "Alice"; }`  
D) `public int add(int a, int b) { }`  

**Answer:** C

**Explanation:**
Option C is valid. Option A has duplicate parameter names (error). Option B is void but returns a value (error). Option D doesn't return a value but declares int return type (error).

---

### Question 11
What is the output?

```java
public class Test {
    public static void main(String[] args) {
        System.out.println(add(10, 20));
    }
    
    static int add(int a, int b) {
        return a + b;
    }
    
    static double add(int a, int b) {
        return a + b + 0.0;
    }
}
```

A) 30  
B) 30.0  
C) Compilation error  
D) Runtime exception  

**Answer:** C

**Explanation:**
Invalid overloading. Both methods have the same parameter list (int, int). Return type alone cannot differentiate overloaded methods. Compilation error.

---

### Question 12
What happens with this code?

```java
public int calculate(int x) {
    if (x > 0) {
        return x * 2;
    }
}
```

A) Compiles successfully  
B) Compilation error - missing return  
C) Runtime exception  
D) Returns 0 when x <= 0  

**Answer:** B

**Explanation:**
Missing return statement for when x <= 0. All paths in a non-void method must return a value. Compilation error.

---

### Question 13
What is the output?

```java
public class Test {
    static void print(int value) {
        System.out.println("int: " + value);
    }
    
    static void print(double value) {
        System.out.println("double: " + value);
    }
    
    public static void main(String[] args) {
        print(10);
    }
}
```

A) int: 10  
B) double: 10  
C) double: 10.0  
D) Compilation error  

**Answer:** A

**Explanation:**
10 is an int literal, so it exactly matches `print(int value)`. No automatic widening to double when exact match exists.

---

### Question 14
Which statement about method parameters is FALSE?

A) Parameters are local to the method  
B) Parameter names can match instance variables  
C) Parameters can be of any type  
D) Parameters must be final  

**Answer:** D

**Explanation:**
Parameters do NOT have to be final. They can be declared final (e.g., `final int value`) but it's not required.

---

### Question 15
What is the output?

```java
public class Test {
    public static void main(String[] args) {
        int result = add(5);
        System.out.println(result);
    }
    
    static int add(int a) {
        return add(a, 0);
    }
    
    static int add(int a, int b) {
        return a + b;
    }
}
```

A) 5  
B) 0  
C) Compilation error  
D) StackOverflowError  

**Answer:** A

**Explanation:**
Method overloading with chaining. `add(5)` calls `add(5, 0)` which returns 5 + 0 = 5.

---

### Question 16
What is the output?

```java
public class Test {
    public static void main(String[] args) {
        StringBuilder sb = new StringBuilder("Hello");
        modify(sb);
        System.out.println(sb);
    }
    
    static void modify(StringBuilder builder) {
        builder.append(" World");
    }
}
```

A) Hello  
B) Hello World  
C) Compilation error  
D) Runtime exception  

**Answer:** B

**Explanation:**
StringBuilder is mutable. The method modifies the actual object (not reassigning the reference). Output: Hello World

---

### Question 17
Which is the correct way to define a method that returns nothing?

A) `public null doSomething() { }`  
B) `public void doSomething() { }`  
C) `public empty doSomething() { }`  
D) `public doSomething() { }`  

**Answer:** B

**Explanation:**
`void` indicates a method returns no value. Options A, C, and D use invalid keywords/syntax.

---

### Question 18
What is the output?

```java
public class Test {
    int value;
    
    Test(int value) {
        value = value;
    }
    
    public static void main(String[] args) {
        Test t = new Test(10);
        System.out.println(t.value);
    }
}
```

A) 10  
B) 0  
C) null  
D) Compilation error  

**Answer:** B

**Explanation:**
Missing `this.` - parameter shadows instance variable. `value = value` assigns parameter to itself. Instance variable remains at default value 0.

---

### Question 19
What is valid method overloading based on?

A) Return type only  
B) Method name only  
C) Parameter list (type, count, order)  
D) Access modifier  

**Answer:** C

**Explanation:**
Method overloading requires different parameter lists (different types, count, or order). Return type, access modifiers, and method names alone are not sufficient.

---

### Question 20
What is the output?

```java
public class Test {
    public static void main(String[] args) {
        int[] arr = {1, 2, 3};
        change(arr);
        System.out.println(arr.length);
    }
    
    static void change(int[] array) {
        array = new int[]{10, 20};
    }
}
```

A) 2  
B) 3  
C) 0  
D) Compilation error  

**Answer:** B

**Explanation:**
Reassignment inside the method creates a new local array reference but doesn't affect the caller's reference. Original array length remains 3.

---

## 📊 Scoring Guide

**Score Interpretation:**
- **18-20 (90-100%)**: Excellent! You have mastered methods and parameters.
- **16-17 (80-89%)**: Good! Review the questions you missed.
- **14-15 (70-79%)**: Fair. Revisit the theory and practice more.
- **Below 14 (< 70%)**: Need more study. Review the theory document carefully.

---

## 🎯 Common Mistakes to Avoid

1. **Pass by value confusion** - Java passes value copies (primitives) or reference value copies (objects)
2. **Overloading rules** - parameter list must differ, not just return type
3. **Missing return statements** - all paths must return for non-void methods
4. **Unreachable code** - code after return is unreachable
5. **Parameter shadowing** - use `this.` to access instance variables
6. **Immutable objects** - String, Integer, etc. cannot be modified
7. **Array/object modification** - can modify contents but not reassign caller's reference

---

## Next Steps

✅ **Scored 16+?** Move to [Variable Arguments and Method References](11-variable-arguments.md)

⚠️ **Scored below 16?** Review [Methods and Parameters Theory](10-methods-parameters.md) and retake this quiz.

---

**Good luck!** ☕
