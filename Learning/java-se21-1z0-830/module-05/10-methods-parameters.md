# Module 5.2: Methods and Parameters

## 📚 Table of Contents
1. [Introduction to Methods](#introduction-to-methods)
2. [Method Declaration](#method-declaration)
3. [Method Parameters](#method-parameters)
4. [Return Values](#return-values)
5. [Method Overloading](#method-overloading)
6. [Pass by Value](#pass-by-value)
7. [Variable Scope](#variable-scope)
8. [Best Practices](#best-practices)
9. [Common Pitfalls](#common-pitfalls)

---

## Introduction to Methods

Methods are blocks of code that perform specific tasks. They promote code reuse and organization.

### Why Use Methods?

- **Reusability** - Write once, use many times
- **Organization** - Break complex logic into manageable pieces
- **Abstraction** - Hide implementation details
- **Maintainability** - Easier to update and debug

---

## Method Declaration

### Basic Method Syntax

```java
accessModifier returnType methodName(parameters) {
    // method body
    return value;  // if returnType is not void
}
```

### Method Components

```java
public int calculateSum(int a, int b) {
    int sum = a + b;
    return sum;
}

// public - access modifier
// int - return type
// calculateSum - method name
// (int a, int b) - parameters
// return sum - return statement
```

### Void Methods

```java
public void printMessage(String message) {
    System.out.println(message);
    // No return statement needed
}

public void greet() {
    System.out.println("Hello!");
    return;  // Optional for void methods
}
```

### Methods with Return Values

```java
public int add(int a, int b) {
    return a + b;
}

public boolean isEven(int number) {
    return number % 2 == 0;
}

public String getFullName(String first, String last) {
    return first + " " + last;
}
```

---

## Method Parameters

### No Parameters

```java
public void sayHello() {
    System.out.println("Hello!");
}

sayHello();  // Call with no arguments
```

### Single Parameter

```java
public void greet(String name) {
    System.out.println("Hello, " + name);
}

greet("Alice");  // Hello, Alice
```

### Multiple Parameters

```java
public int add(int a, int b, int c) {
    return a + b + c;
}

int result = add(10, 20, 30);  // 60
```

### Parameter Types

```java
public void processData(int id, String name, double salary, boolean active) {
    // Parameters can be of any type
}

public void printArray(int[] numbers) {
    for (int num : numbers) {
        System.out.println(num);
    }
}
```

---

## Return Values

### Primitive Return Types

```java
public int getAge() {
    return 25;
}

public double calculateAverage(int a, int b) {
    return (a + b) / 2.0;
}

public boolean isValid() {
    return true;
}
```

### Object Return Types

```java
public String getName() {
    return "Alice";
}

public List<Integer> getNumbers() {
    return List.of(1, 2, 3, 4, 5);
}

public Person createPerson(String name, int age) {
    return new Person(name, age);
}
```

### Multiple Return Points

```java
public String getGrade(int score) {
    if (score >= 90) {
        return "A";
    } else if (score >= 80) {
        return "B";
    } else if (score >= 70) {
        return "C";
    } else {
        return "F";
    }
}
```

### Early Return

```java
public int divide(int a, int b) {
    if (b == 0) {
        System.out.println("Cannot divide by zero");
        return 0;  // Early return
    }
    return a / b;
}
```

---

## Method Overloading

Method overloading allows multiple methods with the same name but different parameters.

### Overloading by Parameter Count

```java
public int add(int a, int b) {
    return a + b;
}

public int add(int a, int b, int c) {
    return a + b + c;
}

public int add(int a, int b, int c, int d) {
    return a + b + c + d;
}

int sum1 = add(10, 20);           // Calls first method
int sum2 = add(10, 20, 30);       // Calls second method
int sum3 = add(10, 20, 30, 40);   // Calls third method
```

### Overloading by Parameter Type

```java
public void print(int value) {
    System.out.println("Integer: " + value);
}

public void print(double value) {
    System.out.println("Double: " + value);
}

public void print(String value) {
    System.out.println("String: " + value);
}

print(10);        // Integer: 10
print(10.5);      // Double: 10.5
print("Hello");   // String: Hello
```

### Overloading by Parameter Order

```java
public void display(String name, int age) {
    System.out.println(name + " is " + age + " years old");
}

public void display(int age, String name) {
    System.out.println(age + " year old " + name);
}

display("Alice", 25);  // Alice is 25 years old
display(25, "Alice");  // 25 year old Alice
```

### Overloading Rules

1. Must have different parameter lists
2. Can have different return types (but not sufficient alone)
3. Can have different access modifiers
4. Can throw different exceptions

```java
// Valid overloading
public int calculate(int a) { return a * 2; }
public double calculate(double a) { return a * 2; }

// Invalid - only return type differs
// public int process(int a) { return a; }
// public double process(int a) { return a; }  // Compilation error
```

---

## Pass by Value

Java is **always pass by value**. For primitives, the value is copied. For objects, the reference value is copied.

### Primitives - Pass by Value

```java
public void modify(int number) {
    number = 100;  // Modifies local copy only
}

int x = 10;
modify(x);
System.out.println(x);  // 10 (unchanged)
```

### Objects - Pass by Reference Value

```java
public void modifyPerson(Person person) {
    person.setAge(30);  // Modifies the object
}

public void reassignPerson(Person person) {
    person = new Person("Bob", 25);  // Reassigns local reference only
}

Person p = new Person("Alice", 20);
modifyPerson(p);
System.out.println(p.getAge());  // 30 (object modified)

reassignPerson(p);
System.out.println(p.getName());  // Alice (original reference unchanged)
```

### Arrays - Pass by Reference Value

```java
public void modifyArray(int[] arr) {
    arr[0] = 100;  // Modifies the array
}

public void reassignArray(int[] arr) {
    arr = new int[]{10, 20, 30};  // Reassigns local reference only
}

int[] numbers = {1, 2, 3};
modifyArray(numbers);
System.out.println(numbers[0]);  // 100 (array modified)

reassignArray(numbers);
System.out.println(numbers.length);  // 3 (original array unchanged)
```

### Strings - Immutable Objects

```java
public void modifyString(String str) {
    str = "Modified";  // Reassigns local reference only
}

String text = "Original";
modifyString(text);
System.out.println(text);  // Original (strings are immutable)
```

---

## Variable Scope

### Local Variables

```java
public void method() {
    int localVar = 10;  // Local to this method
    if (true) {
        int blockVar = 20;  // Local to this block
        System.out.println(localVar);  // OK
    }
    // System.out.println(blockVar);  // Error - out of scope
}
```

### Method Parameters

```java
public void calculate(int value) {
    // 'value' is accessible throughout the method
    value = value * 2;
    System.out.println(value);
}
// 'value' not accessible here
```

### Instance Variables

```java
public class Calculator {
    private int result;  // Instance variable - accessible to all instance methods
    
    public void add(int value) {
        result += value;  // Accessible
    }
    
    public int getResult() {
        return result;  // Accessible
    }
}
```

### Variable Shadowing

```java
public class Example {
    private int value = 10;  // Instance variable
    
    public void method(int value) {  // Parameter shadows instance variable
        int value2 = 20;  // Local variable
        
        System.out.println(value);        // Parameter (from argument)
        System.out.println(this.value);   // Instance variable (10)
        System.out.println(value2);       // Local variable (20)
    }
}
```

---

## Best Practices

### 1. Single Responsibility

```java
// Bad - method does too much
public void processUser(String name, int age, String email) {
    validateName(name);
    validateAge(age);
    validateEmail(email);
    saveToDatabase(name, age, email);
    sendWelcomeEmail(email);
    logActivity(name);
}

// Good - separate methods
public void registerUser(User user) {
    validateUser(user);
    saveUser(user);
    notifyUser(user);
}

private void validateUser(User user) { /* validation logic */ }
private void saveUser(User user) { /* database logic */ }
private void notifyUser(User user) { /* notification logic */ }
```

### 2. Descriptive Names

```java
// Bad
public int calc(int a, int b) {
    return a + b;
}

// Good
public int calculateTotalPrice(int itemPrice, int quantity) {
    return itemPrice * quantity;
}
```

### 3. Limit Parameter Count

```java
// Bad - too many parameters
public void createUser(String firstName, String lastName, String email, 
                       String phone, int age, String address, String city, 
                       String state, String zip) {
    // ...
}

// Good - use object
public void createUser(User user) {
    // ...
}
```

### 4. Return Early

```java
// Bad - nested conditions
public boolean isValid(String input) {
    if (input != null) {
        if (input.length() > 0) {
            if (input.length() <= 100) {
                return true;
            }
        }
    }
    return false;
}

// Good - early returns
public boolean isValid(String input) {
    if (input == null) return false;
    if (input.length() == 0) return false;
    if (input.length() > 100) return false;
    return true;
}
```

### 5. Avoid Side Effects

```java
// Bad - modifies global state
private int counter = 0;
public int add(int a, int b) {
    counter++;  // Side effect
    return a + b;
}

// Good - pure function
public int add(int a, int b) {
    return a + b;  // No side effects
}
```

---

## Common Pitfalls

### 1. Missing Return Statement

```java
// Compilation error - missing return for some paths
public int getMax(int a, int b) {
    if (a > b) {
        return a;
    }
    // Missing return for when a <= b
}

// Fixed
public int getMax(int a, int b) {
    if (a > b) {
        return a;
    }
    return b;  // Always has a return
}
```

### 2. Unreachable Code

```java
public int calculate(int x) {
    return x * 2;
    // System.out.println("Done");  // Unreachable - compilation error
}
```

### 3. Wrong Return Type

```java
// Compilation error - cannot convert String to int
public int getName() {
    return "Alice";  // Error
}

// Fixed
public String getName() {
    return "Alice";
}
```

### 4. Modifying Parameters (Confusion)

```java
public void increment(int value) {
    value++;  // Only modifies local copy
}

int num = 10;
increment(num);
System.out.println(num);  // Still 10 (not 11)
```

### 5. Overloading Confusion

```java
public void print(int value) {
    System.out.println("int: " + value);
}

public void print(long value) {
    System.out.println("long: " + value);
}

print(10);    // Calls print(int)
print(10L);   // Calls print(long)
print(10.0);  // Compilation error - no matching method
```

---

## Summary

### Method Declaration
- **Syntax:** `accessModifier returnType name(parameters) { body }`
- **Return:** Use `return` for non-void methods
- **Void:** Methods that don't return a value

### Parameters
- Values passed to methods
- Can be primitives or objects
- Multiple parameters separated by commas

### Method Overloading
- Same name, different parameters
- Different parameter count, type, or order
- Return type alone is not sufficient

### Pass by Value
- Primitives: value is copied
- Objects: reference value is copied
- Cannot reassign caller's reference

### Scope
- **Local:** Variables in method/block
- **Parameters:** Method arguments
- **Instance:** Class-level variables

---

## Practice Questions

Ready to test your knowledge? Proceed to [Methods Practice Questions](10-practice-questions.md)!

---

**Next:** [Practice Questions - Methods and Parameters](10-practice-questions.md)  
**Previous:** [Classes and Objects Practice](09-practice-questions.md)

---

**Good luck!** ☕
