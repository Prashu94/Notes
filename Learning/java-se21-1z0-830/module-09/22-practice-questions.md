# Module 9: Arrays and ArrayList - Practice Questions

## Practice Questions (20)

### Question 1
What is the output?
```java
int[] arr = {1, 2, 3, 4, 5};
System.out.println(arr.length);
```
A) 4  
B) 5  
C) Compilation error  
D) Runtime exception

**Answer: B) 5**

**Explanation**: The `.length` property of an array returns the number of elements. The array has 5 elements, so `arr.length` is 5.

---

### Question 2
Which is the correct way to declare an array?
A) `int[] arr;`  
B) `int arr[];`  
C) `Both A and B`  
D) `Neither A nor B`

**Answer: C) Both A and B**

**Explanation**: Both syntaxes are valid in Java. `int[] arr;` is preferred (Java style), while `int arr[];` is C-style but also valid.

---

### Question 3
What is the output?
```java
ArrayList<Integer> list = new ArrayList<>();
list.add(10);
list.add(20);
list.add(1, 15);
System.out.println(list);
```
A) [10, 20, 15]  
B) [10, 15, 20]  
C) [15, 10, 20]  
D) Compilation error

**Answer: B) [10, 15, 20]**

**Explanation**: `add(1, 15)` inserts 15 at index 1, shifting 20 to index 2. Result: [10, 15, 20].

---

### Question 4
What happens when this code runs?
```java
int[] arr = new int[3];
System.out.println(arr[3]);
```
A) 0  
B) null  
C) ArrayIndexOutOfBoundsException  
D) Compilation error

**Answer: C) ArrayIndexOutOfBoundsException**

**Explanation**: Array indices range from 0 to length-1. For an array of size 3, valid indices are 0, 1, 2. Accessing index 3 throws ArrayIndexOutOfBoundsException at runtime.

---

### Question 5
Which statement about ArrayList is TRUE?
A) ArrayList can store primitive types directly  
B) ArrayList has fixed size  
C) ArrayList uses .size() method to get the number of elements  
D) ArrayList is faster than arrays for access

**Answer: C) ArrayList uses .size() method to get the number of elements**

**Explanation**: ArrayList uses `.size()` method (not `.length` property). ArrayList cannot store primitives directly (needs wrapper classes), has dynamic size, and is slightly slower than arrays for element access.

---

### Question 6
What is the output?
```java
import java.util.Arrays;

int[] arr = {5, 2, 8, 1, 9};
Arrays.sort(arr);
System.out.println(Arrays.binarySearch(arr, 8));
```
A) 2  
B) 3  
C) 4  
D) -1

**Answer: B) 3**

**Explanation**: After sorting, arr becomes [1, 2, 5, 8, 9]. The value 8 is at index 3. Binary search returns 3.

---

### Question 7
What is the default value of elements in an integer array?
```java
int[] arr = new int[5];
```
A) null  
B) 0  
C) -1  
D) Undefined

**Answer: B) 0**

**Explanation**: Primitive arrays are initialized with default values. For int arrays, the default is 0. For object arrays, it's null. For boolean, it's false. For double/float, it's 0.0.

---

### Question 8
What is the result?
```java
ArrayList<String> list = new ArrayList<>();
list.add("A");
list.add("B");
list.add("C");
list.remove(1);
System.out.println(list);
```
A) [A, B, C]  
B) [A, C]  
C) [B, C]  
D) [A, B]

**Answer: B) [A, C]**

**Explanation**: `remove(1)` removes the element at index 1 ("B"). The list becomes [A, C].

---

### Question 9
Which method is used to convert ArrayList to array?
A) `toArray()`  
B) `asArray()`  
C) `convertToArray()`  
D) `getArray()`

**Answer: A) `toArray()`**

**Explanation**: The `toArray()` method converts an ArrayList to an array. Usage: `String[] arr = list.toArray(new String[0]);`

---

### Question 10
What is the output?
```java
int[][] matrix = {{1, 2}, {3, 4}, {5, 6}};
System.out.println(matrix.length);
System.out.println(matrix[0].length);
```
A) 3, 2  
B) 2, 3  
C) 6, 2  
D) 2, 6

**Answer: A) 3, 2**

**Explanation**: `matrix.length` returns the number of rows (3). `matrix[0].length` returns the number of columns in the first row (2).

---

### Question 11
What happens when you compile this code?
```java
ArrayList<int> list = new ArrayList<>();
```
A) Compiles successfully  
B) Compilation error - cannot use primitive type with generics  
C) Runtime exception  
D) Creates empty list

**Answer: B) Compilation error - cannot use primitive type with generics**

**Explanation**: Generics don't support primitive types. Use wrapper class: `ArrayList<Integer> list = new ArrayList<>();`

---

### Question 12
What is the output?
```java
String[] arr = {"A", "B", "C"};
for (String s : arr) {
    s = "X";
}
System.out.println(arr[0]);
```
A) X  
B) A  
C) Compilation error  
D) null

**Answer: B) A**

**Explanation**: The enhanced for loop variable `s` is a copy. Modifying `s` doesn't affect the array. The array remains unchanged, so `arr[0]` is still "A".

---

### Question 13
Which Arrays method is used to compare two arrays for equality?
A) `Arrays.compare()`  
B) `Arrays.equals()`  
C) `Arrays.same()`  
D) `Arrays.match()`

**Answer: B) `Arrays.equals()`**

**Explanation**: `Arrays.equals(arr1, arr2)` compares two arrays for equality. For multi-dimensional arrays, use `Arrays.deepEquals()`.

---

### Question 14
What is the result?
```java
ArrayList<String> list = new ArrayList<>();
System.out.println(list.isEmpty());
list.add("A");
System.out.println(list.isEmpty());
```
A) true, true  
B) false, false  
C) true, false  
D) false, true

**Answer: C) true, false**

**Explanation**: Initially the list is empty (`isEmpty()` returns true). After adding "A", it's not empty (`isEmpty()` returns false).

---

### Question 15
What is the output?
```java
int[] arr = {1, 2, 3};
System.out.println(arr);
```
A) [1, 2, 3]  
B) 1, 2, 3  
C) Hashcode/memory address  
D) Compilation error

**Answer: C) Hashcode/memory address**

**Explanation**: Printing an array directly prints its memory address/hashcode (e.g., `[I@15db9742`). Use `Arrays.toString(arr)` to print the contents.

---

### Question 16
What happens with this code?
```java
ArrayList<String> list = new ArrayList<>(Arrays.asList("A", "B", "C"));
list.remove("B");
System.out.println(list.indexOf("C"));
```
A) 1  
B) 2  
C) -1  
D) 0

**Answer: A) 1**

**Explanation**: After removing "B", the list becomes [A, C]. The index of "C" is 1.

---

### Question 17
Which statement about array initialization is TRUE?
A) `int[] arr = {1, 2, 3};` is valid  
B) `int[] arr = new int[]{1, 2, 3};` is valid  
C) Both A and B are valid  
D) Neither A nor B is valid

**Answer: C) Both A and B are valid**

**Explanation**: Both syntaxes are valid for array initialization. The first is shorthand, the second is explicit anonymous array creation.

---

### Question 18
What is the output?
```java
ArrayList<Integer> list = new ArrayList<>();
list.add(1);
list.add(2);
list.add(3);
list.set(1, 10);
System.out.println(list);
```
A) [1, 10, 3]  
B) [1, 2, 10]  
C) [10, 2, 3]  
D) [1, 2, 3, 10]

**Answer: A) [1, 10, 3]**

**Explanation**: `set(1, 10)` replaces the element at index 1 with 10. The list becomes [1, 10, 3].

---

### Question 19
What is the result of Arrays.binarySearch on an unsorted array?
```java
int[] arr = {5, 2, 8, 1, 9};
int result = Arrays.binarySearch(arr, 8);
```
A) Correct index always  
B) Undefined behavior  
C) Compilation error  
D) Always returns -1

**Answer: B) Undefined behavior**

**Explanation**: `Arrays.binarySearch()` requires a sorted array. On an unsorted array, the result is undefined and unpredictable.

---

### Question 20
What is the output?
```java
ArrayList<String> list = new ArrayList<>();
list.add("A");
list.add("B");
list.add("A");
System.out.println(list.lastIndexOf("A"));
```
A) 0  
B) 1  
C) 2  
D) -1

**Answer: C) 2**

**Explanation**: `lastIndexOf()` returns the index of the last occurrence. "A" appears at indices 0 and 2. The last occurrence is at index 2.

---

## Answer Summary
1. B  2. C  3. B  4. C  5. C  
6. B  7. B  8. B  9. A  10. A  
11. B  12. B  13. B  14. C  15. C  
16. A  17. C  18. A  19. B  20. C
