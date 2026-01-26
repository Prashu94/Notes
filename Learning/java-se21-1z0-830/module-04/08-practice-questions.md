# Module 4.2: Loops and Iteration - Practice Questions

## 📝 Practice Exam (20 Questions)

**Time Limit:** 30 minutes  
**Passing Score:** 16/20 (80%)

---

### Question 1
What is the output?

```java
for (int i = 0; i < 3; i++) {
    System.out.print(i + " ");
}
```

A) 0 1 2  
B) 0 1 2 3  
C) 1 2 3  
D) Compilation error  

**Answer:** A

**Explanation:**
Loop executes while i < 3. When i is 0, 1, 2, the condition is true. When i becomes 3, the condition is false and the loop exits. Output: 0 1 2

---

### Question 2
How many times does the loop execute?

```java
int count = 5;
while (count < 5) {
    System.out.println(count);
    count++;
}
```

A) 0 times  
B) 1 time  
C) 5 times  
D) Infinite  

**Answer:** A

**Explanation:**
The condition `count < 5` is false initially (5 is not < 5), so the loop body never executes.

---

### Question 3
What is the output?

```java
int x = 10;
do {
    System.out.println(x);
    x--;
} while (x < 5);
```

A) Nothing  
B) 10  
C) 10 9 8 7 6 5  
D) Infinite loop  

**Answer:** B

**Explanation:**
Do-while executes at least once. It prints 10, then x becomes 9. The condition x < 5 is false (9 is not < 5), so it stops.

---

### Question 4
What is the output?

```java
for (int i = 0; i < 5; i++) {
    if (i == 2) {
        continue;
    }
    System.out.print(i + " ");
}
```

A) 0 1 2 3 4  
B) 0 1 3 4  
C) 2  
D) 0 1  

**Answer:** B

**Explanation:**
Continue skips the current iteration. When i is 2, continue is executed, skipping the print statement for 2. Output: 0 1 3 4

---

### Question 5
What is the output?

```java
for (int i = 0; i < 5; i++) {
    if (i == 3) {
        break;
    }
    System.out.print(i + " ");
}
```

A) 0 1 2  
B) 0 1 2 3  
C) 3  
D) 0 1 2 3 4  

**Answer:** A

**Explanation:**
Break exits the loop immediately. When i is 3, break is executed, terminating the loop. It prints 0, 1, 2 before breaking.

---

### Question 6
How many times does this loop execute?

```java
int i = 0;
while (i < 10) {
    i += 2;
}
```

A) 5 times  
B) 10 times  
C) 11 times  
D) Infinite  

**Answer:** A

**Explanation:**
i starts at 0. Loop executes when i is 0, 2, 4, 6, 8 (5 times). When i becomes 10, the condition is false.

---

### Question 7
What is the output?

```java
int[] numbers = {1, 2, 3};
for (int num : numbers) {
    num = num * 2;
}
System.out.println(Arrays.toString(numbers));
```

A) [1, 2, 3]  
B) [2, 4, 6]  
C) [0, 0, 0]  
D) Compilation error  

**Answer:** A

**Explanation:**
Enhanced for loop copies values. Modifying `num` doesn't affect the original array. The array remains [1, 2, 3].

---

### Question 8
What is the output?

```java
for (int i = 5; i > 0; i--) {
    System.out.print(i + " ");
}
```

A) 5 4 3 2 1  
B) 0 1 2 3 4 5  
C) 1 2 3 4 5  
D) Infinite loop  

**Answer:** A

**Explanation:**
Loop starts at 5 and decrements. It executes while i > 0, printing 5, 4, 3, 2, 1.

---

### Question 9
What happens with this code?

```java
List<String> list = new ArrayList<>(List.of("A", "B", "C"));
for (String s : list) {
    if (s.equals("B")) {
        list.remove(s);
    }
}
```

A) Removes "B" successfully  
B) ConcurrentModificationException  
C) Compilation error  
D) Nothing happens  

**Answer:** B

**Explanation:**
Modifying a collection while iterating with enhanced for loop throws ConcurrentModificationException. Use Iterator.remove() instead.

---

### Question 10
What is the output?

```java
outer:
for (int i = 0; i < 2; i++) {
    for (int j = 0; j < 2; j++) {
        if (i == 1 && j == 0) {
            break outer;
        }
        System.out.println(i + "," + j);
    }
}
```

A) 0,0 0,1  
B) 0,0 0,1 1,0  
C) 0,0 0,1 1,0 1,1  
D) 0,0  

**Answer:** A

**Explanation:**
Labeled break exits the outer loop. Prints (0,0), (0,1), then when i=1 and j=0, it breaks the outer loop entirely.

---

### Question 11
What is the output?

```java
for (int i = 0; i < 3; i++) {
    for (int j = 0; j < 2; j++) {
        System.out.print("*");
    }
    System.out.println();
}
```

A) ******  
B) **  
   **  
   **  
C) ***  
   ***  
D) Compilation error  

**Answer:** B

**Explanation:**
Outer loop runs 3 times. Inner loop prints 2 stars each time, followed by a newline. Output:
```
**
**
**
```

---

### Question 12
What is the value of `count` after this code?

```java
int count = 0;
for (int i = 0; i < 5; i++) {
    count++;
}
```

A) 0  
B) 4  
C) 5  
D) Compilation error  

**Answer:** C

**Explanation:**
Loop executes 5 times (i = 0, 1, 2, 3, 4). Count is incremented each time, resulting in count = 5.

---

### Question 13
What is the output?

```java
int i = 0;
while (i < 3) {
    System.out.print(i++ + " ");
}
```

A) 0 1 2  
B) 1 2 3  
C) 0 1 2 3  
D) Infinite loop  

**Answer:** A

**Explanation:**
`i++` uses the current value (0, 1, 2) for printing, then increments. Loop prints 0, 1, 2.

---

### Question 14
Which loop guarantees at least one execution?

A) while  
B) for  
C) do-while  
D) for-each  

**Answer:** C

**Explanation:**
Do-while checks the condition AFTER executing the loop body, guaranteeing at least one execution regardless of the condition.

---

### Question 15
What is the output?

```java
for (int i = 0; i < 10; i++) {
    if (i == 5) {
        break;
    }
    if (i % 2 == 0) {
        continue;
    }
    System.out.print(i + " ");
}
```

A) 1 3  
B) 1 3 5  
C) 1 3 5 7 9  
D) 0 2 4  

**Answer:** A

**Explanation:**
Loop prints odd numbers until i = 5. i = 0 (even, continue), 1 (odd, print), 2 (even, continue), 3 (odd, print), 4 (even, continue), 5 (break). Output: 1 3

---

### Question 16
What is the output?

```java
String[] names = {"Alice", "Bob", "Charlie"};
for (String name : names) {
    System.out.print(name.charAt(0));
}
```

A) ABC  
B) AliceBobCharlie  
C) 0 1 2  
D) Compilation error  

**Answer:** A

**Explanation:**
For-each iterates through the array. charAt(0) gets the first character of each name: A, B, C. Output: ABC

---

### Question 17
How many times does this loop execute?

```java
for (int i = 1; i <= 100; i *= 2) {
    System.out.println(i);
}
```

A) 7 times  
B) 50 times  
C) 100 times  
D) Infinite  

**Answer:** A

**Explanation:**
i doubles each iteration: 1, 2, 4, 8, 16, 32, 64 (7 values <= 100). Next would be 128, which is > 100.

---

### Question 18
What is the output?

```java
for (int i = 0; i < 5; ) {
    System.out.print(i + " ");
    i++;
}
```

A) 0 1 2 3 4  
B) 1 2 3 4 5  
C) Infinite loop  
D) Compilation error  

**Answer:** A

**Explanation:**
The update expression can be omitted from the for loop header and placed in the body instead. This works correctly and prints 0 1 2 3 4.

---

### Question 19
What is the output?

```java
int sum = 0;
for (int i = 1; i <= 5; i++) {
    sum += i;
}
System.out.println(sum);
```

A) 10  
B) 15  
C) 5  
D) 0  

**Answer:** B

**Explanation:**
Sum of 1 + 2 + 3 + 4 + 5 = 15.

---

### Question 20
What is the output?

```java
outer:
for (int i = 0; i < 3; i++) {
    for (int j = 0; j < 3; j++) {
        if (j == 1) {
            continue outer;
        }
        System.out.print(i + "" + j + " ");
    }
}
```

A) 00 10 20  
B) 00 01 02 10 11 12 20 21 22  
C) 00 11 22  
D) 00 01 10 11 20 21  

**Answer:** A

**Explanation:**
Labeled continue skips to the next iteration of the outer loop. When j=1, it continues outer, skipping j=2. Only prints when j=0: 00, 10, 20.

---

## 📊 Scoring Guide

**Score Interpretation:**
- **18-20 (90-100%)**: Excellent! You have mastered loops and iteration.
- **16-17 (80-89%)**: Good! Review the questions you missed.
- **14-15 (70-79%)**: Fair. Revisit the theory and practice more.
- **Below 14 (< 70%)**: Need more study. Review the theory document carefully.

---

## 🎯 Common Mistakes to Avoid

1. **Off-by-one errors** - careful with < vs <=
2. **Modifying collections** while iterating with for-each
3. **Forgetting to increment** in while loops (infinite loop)
4. **Confusing break and continue** - break exits, continue skips
5. **Variable scope** - loop variables not accessible outside
6. **Floating-point counters** - precision issues
7. **For-each limitations** - can't modify array elements

---

## Module 4 Complete! 🎉

You've completed the Control Flow module covering:
- ✅ If-else statements and ternary operator
- ✅ Switch statements and expressions
- ✅ Pattern matching for switch (Java 21)
- ✅ While, do-while, for, and for-each loops
- ✅ Break, continue, and labels

**Total Practice Questions:** 40/40 ✓

---

## Next Steps

✅ **Scored 16+ on both quizzes?** Move to [Module 5: OOP Basics](../module-05/09-classes-objects.md)

⚠️ **Scored below 16?** Review the theory documents and retake the quizzes.

---

**Good luck!** ☕
