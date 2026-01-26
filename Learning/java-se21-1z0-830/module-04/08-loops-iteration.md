# Module 4.2: Loops and Iteration

## 📚 Table of Contents
1. [Introduction](#introduction)
2. [While Loop](#while-loop)
3. [Do-While Loop](#do-while-loop)
4. [For Loop](#for-loop)
5. [Enhanced For Loop (For-Each)](#enhanced-for-loop-for-each)
6. [Loop Control Statements](#loop-control-statements)
7. [Nested Loops](#nested-loops)
8. [Best Practices](#best-practices)
9. [Common Pitfalls](#common-pitfalls)

---

## Introduction

Loops allow code to execute repeatedly. Java provides several loop constructs: while, do-while, for, and enhanced for (for-each).

---

## While Loop

While loop executes as long as the condition is true. The condition is checked **before** each iteration.

### Basic While Loop

```java
int count = 0;
while (count < 5) {
    System.out.println(count);
    count++;
}
// Prints: 0 1 2 3 4 (on separate lines)
```

### While with Complex Condition

```java
int sum = 0;
int num = 1;
while (num <= 10 && sum < 30) {
    sum += num;
    num++;
}
System.out.println("Sum: " + sum);  // Sum: 36
System.out.println("Num: " + num);  // Num: 9
```

### Infinite Loop

```java
// Infinite loop - never exits
while (true) {
    System.out.println("Forever");
    // Need break or return to exit
}
```

### While with Empty Body

```java
int count = 0;
while (++count < 5);  // Empty body
System.out.println(count);  // 5
```

---

## Do-While Loop

Do-while loop executes at least once because the condition is checked **after** each iteration.

### Basic Do-While

```java
int count = 0;
do {
    System.out.println(count);
    count++;
} while (count < 5);
// Prints: 0 1 2 3 4
```

### Do-While vs While

```java
// While loop - never executes if condition is initially false
int x = 10;
while (x < 5) {
    System.out.println(x);
}
// Prints nothing

// Do-while - executes at least once
int y = 10;
do {
    System.out.println(y);
} while (y < 5);
// Prints: 10 (once, then stops)
```

### Practical Use Case

```java
Scanner scanner = new Scanner(System.in);
String input;
do {
    System.out.print("Enter 'quit' to exit: ");
    input = scanner.nextLine();
} while (!input.equals("quit"));
// Always asks at least once
```

---

## For Loop

For loop is ideal for counted iterations. It has three parts: initialization, condition, and update.

### Basic For Loop

```java
for (int i = 0; i < 5; i++) {
    System.out.println(i);
}
// Prints: 0 1 2 3 4
```

### For Loop Structure

```java
for (initialization; condition; update) {
    // body
}

// Example breakdown:
for (int i = 0;    // 1. Initialize (once)
     i < 5;        // 2. Check condition (before each iteration)
     i++           // 3. Update (after each iteration)
) {
    System.out.println(i);  // 4. Body
}
```

### Multiple Variables

```java
for (int i = 0, j = 10; i < j; i++, j--) {
    System.out.println(i + " " + j);
}
// Prints:
// 0 10
// 1 9
// 2 8
// 3 7
// 4 6
```

### Reverse Loop

```java
for (int i = 5; i > 0; i--) {
    System.out.println(i);
}
// Prints: 5 4 3 2 1
```

### Empty Parts

```java
// Initialization outside
int i = 0;
for (; i < 5; i++) {
    System.out.println(i);
}

// Update inside body
for (int j = 0; j < 5;) {
    System.out.println(j);
    j++;
}

// All parts empty (infinite loop)
for (;;) {
    System.out.println("Forever");
    break;  // Need break to exit
}
```

---

## Enhanced For Loop (For-Each)

Enhanced for loop (for-each) iterates over arrays and collections without explicit indexing.

### Array Iteration

```java
int[] numbers = {1, 2, 3, 4, 5};
for (int num : numbers) {
    System.out.println(num);
}
// Prints: 1 2 3 4 5
```

### Collection Iteration

```java
List<String> names = List.of("Alice", "Bob", "Charlie");
for (String name : names) {
    System.out.println(name);
}
// Prints: Alice Bob Charlie
```

### String Array

```java
String[] fruits = {"apple", "banana", "cherry"};
for (String fruit : fruits) {
    System.out.println(fruit.toUpperCase());
}
// Prints: APPLE BANANA CHERRY
```

### Limitations

```java
// Cannot modify the array/collection elements directly
int[] numbers = {1, 2, 3};
for (int num : numbers) {
    num = num * 2;  // Doesn't modify the array
}
System.out.println(Arrays.toString(numbers));  // [1, 2, 3] - unchanged

// Need regular for loop to modify
for (int i = 0; i < numbers.length; i++) {
    numbers[i] = numbers[i] * 2;
}
System.out.println(Arrays.toString(numbers));  // [2, 4, 6]
```

### For-Each vs Regular For

| Feature | For-Each | Regular For |
|---------|----------|-------------|
| **Index access** | No | Yes |
| **Modify elements** | No | Yes |
| **Reverse iteration** | No | Yes |
| **Readability** | High | Medium |
| **Use case** | Read-only iteration | Indexed/modified access |

---

## Loop Control Statements

### Break

Break exits the **current** loop immediately.

```java
for (int i = 0; i < 10; i++) {
    if (i == 5) {
        break;  // Exit loop when i is 5
    }
    System.out.println(i);
}
// Prints: 0 1 2 3 4
```

### Continue

Continue skips the **current iteration** and moves to the next.

```java
for (int i = 0; i < 5; i++) {
    if (i == 2) {
        continue;  // Skip when i is 2
    }
    System.out.println(i);
}
// Prints: 0 1 3 4 (skips 2)
```

### Break vs Continue

```java
// Break - exits loop entirely
for (int i = 0; i < 5; i++) {
    if (i == 2) break;
    System.out.println(i);
}
// Output: 0 1

// Continue - skips current iteration
for (int i = 0; i < 5; i++) {
    if (i == 2) continue;
    System.out.println(i);
}
// Output: 0 1 3 4
```

### Labeled Break

Break can target an outer loop using labels.

```java
outer:
for (int i = 0; i < 3; i++) {
    for (int j = 0; j < 3; j++) {
        if (i == 1 && j == 1) {
            break outer;  // Breaks outer loop
        }
        System.out.println(i + "," + j);
    }
}
// Prints:
// 0,0
// 0,1
// 0,2
// 1,0
```

### Labeled Continue

```java
outer:
for (int i = 0; i < 3; i++) {
    for (int j = 0; j < 3; j++) {
        if (j == 1) {
            continue outer;  // Continues outer loop
        }
        System.out.println(i + "," + j);
    }
}
// Prints:
// 0,0
// 1,0
// 2,0
```

---

## Nested Loops

Nested loops are loops inside loops.

### Multiplication Table

```java
for (int i = 1; i <= 5; i++) {
    for (int j = 1; j <= 5; j++) {
        System.out.print((i * j) + "\t");
    }
    System.out.println();
}
// Prints:
// 1   2   3   4   5
// 2   4   6   8   10
// 3   6   9   12  15
// 4   8   12  16  20
// 5   10  15  20  25
```

### Pattern Printing

```java
for (int i = 1; i <= 4; i++) {
    for (int j = 1; j <= i; j++) {
        System.out.print("* ");
    }
    System.out.println();
}
// Prints:
// *
// * *
// * * *
// * * * *
```

### Searching 2D Array

```java
int[][] matrix = {
    {1, 2, 3},
    {4, 5, 6},
    {7, 8, 9}
};

int target = 5;
boolean found = false;

outer:
for (int i = 0; i < matrix.length; i++) {
    for (int j = 0; j < matrix[i].length; j++) {
        if (matrix[i][j] == target) {
            System.out.println("Found at (" + i + "," + j + ")");
            found = true;
            break outer;  // Exit both loops
        }
    }
}
// Prints: Found at (1,1)
```

---

## Best Practices

### 1. Choose the Right Loop

```java
// For-each for simple iteration
String[] names = {"Alice", "Bob", "Charlie"};
for (String name : names) {
    System.out.println(name);
}

// Regular for when you need index
for (int i = 0; i < names.length; i++) {
    System.out.println(i + ": " + names[i]);
}

// While for condition-based loops
while (hasMoreData()) {
    processData();
}

// Do-while when you need at least one execution
do {
    getUserInput();
} while (!isValid());
```

### 2. Avoid Infinite Loops

```java
// Bad - infinite loop
for (int i = 0; i < 10; i--) {  // i-- instead of i++
    // Never reaches 10
}

// Good - proper increment
for (int i = 0; i < 10; i++) {
    // Executes 10 times
}
```

### 3. Minimize Work in Loops

```java
// Bad - expensive call in condition
for (int i = 0; i < list.size(); i++) {  // size() called every iteration
    process(list.get(i));
}

// Good - cache size
int size = list.size();
for (int i = 0; i < size; i++) {
    process(list.get(i));
}

// Best - use for-each when applicable
for (Item item : list) {
    process(item);
}
```

### 4. Use Descriptive Loop Variables

```java
// Bad
for (int i = 0; i < students.length; i++) {
    for (int j = 0; j < grades.length; j++) {
        // Hard to understand
    }
}

// Good
for (int studentIndex = 0; studentIndex < students.length; studentIndex++) {
    for (int gradeIndex = 0; gradeIndex < grades.length; gradeIndex++) {
        // Clear intent
    }
}

// Best - for-each when possible
for (Student student : students) {
    for (Grade grade : student.getGrades()) {
        // Very clear
    }
}
```

---

## Common Pitfalls

### 1. Off-by-One Errors

```java
// Wrong - iterates 0-4 (5 times), but array has indices 0-4
int[] arr = new int[5];
for (int i = 0; i <= arr.length; i++) {  // <= is wrong
    arr[i] = i;  // ArrayIndexOutOfBoundsException when i=5
}

// Correct
for (int i = 0; i < arr.length; i++) {  // < is correct
    arr[i] = i;
}
```

### 2. Modifying Collection While Iterating

```java
List<Integer> numbers = new ArrayList<>(List.of(1, 2, 3, 4, 5));

// Wrong - ConcurrentModificationException
for (Integer num : numbers) {
    if (num % 2 == 0) {
        numbers.remove(num);  // Modifying during iteration
    }
}

// Correct - use Iterator
Iterator<Integer> iterator = numbers.iterator();
while (iterator.hasNext()) {
    if (iterator.next() % 2 == 0) {
        iterator.remove();  // Safe removal
    }
}

// Or use removeIf (Java 8+)
numbers.removeIf(num -> num % 2 == 0);
```

### 3. Variable Scope

```java
// Wrong - i not accessible outside loop
for (int i = 0; i < 5; i++) {
    // i is accessible here
}
// System.out.println(i);  // Compilation error - i not in scope

// Correct - declare outside if needed
int i;
for (i = 0; i < 5; i++) {
    // i accessible here
}
System.out.println(i);  // 5
```

### 4. Floating-Point Loop Counter

```java
// Bad - floating-point precision issues
for (double d = 0.0; d < 1.0; d += 0.1) {
    System.out.println(d);
}
// May not print exactly 10 values due to floating-point errors

// Good - use integer counter
for (int i = 0; i < 10; i++) {
    double d = i * 0.1;
    System.out.println(d);
}
```

### 5. Unnecessary Continue at End of Loop

```java
// Redundant - continue at end does nothing
for (int i = 0; i < 5; i++) {
    System.out.println(i);
    continue;  // Unnecessary
}

// Just remove it
for (int i = 0; i < 5; i++) {
    System.out.println(i);
}
```

---

## Summary

| Loop Type | When to Use | Condition Check |
|-----------|-------------|-----------------|
| **while** | Unknown iterations, condition-based | Before iteration |
| **do-while** | At least one execution needed | After iteration |
| **for** | Known iterations, counter-based | Before iteration |
| **for-each** | Iterate collections/arrays (read-only) | N/A |

### Control Statements

- **break**: Exit current loop
- **continue**: Skip current iteration
- **labeled break/continue**: Control outer loops

### Best Practices

1. Use for-each for simple iteration
2. Cache expensive calls outside loop condition
3. Avoid modifying collections while iterating
4. Beware of off-by-one errors
5. Choose appropriate loop type for the task

---

## Practice Questions

Ready to test your knowledge? Proceed to [Loops Practice Questions](08-practice-questions.md)!

---

**Next:** [Practice Questions - Loops and Iteration](08-practice-questions.md)  
**Previous:** [Control Flow Practice Questions](07-practice-questions.md)

---

**Good luck!** ☕
