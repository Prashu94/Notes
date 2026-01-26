# Module 9: Arrays and Collections - Arrays and ArrayList

## Table of Contents
1. [Arrays Introduction](#arrays-introduction)
2. [Array Declaration and Creation](#array-declaration-and-creation)
3. [Array Operations](#array-operations)
4. [Multi-Dimensional Arrays](#multi-dimensional-arrays)
5. [Arrays Class Utility Methods](#arrays-class-utility-methods)
6. [ArrayList Introduction](#arraylist-introduction)
7. [ArrayList Operations](#arraylist-operations)
8. [ArrayList vs Array](#arraylist-vs-array)
9. [Best Practices](#best-practices)

## Arrays Introduction

An **array** is a container object that holds a fixed number of values of a single type. Arrays are **fixed-size** and provide **fast access** to elements by index.

### Key Characteristics

- **Fixed size**: Size determined at creation, cannot change
- **Type-safe**: Stores only declared type
- **Zero-indexed**: First element at index 0
- **Reference type**: Arrays are objects
- **Length property**: `array.length` (not a method)

### Array Types

```java
// Primitive arrays
int[] numbers;
double[] values;
boolean[] flags;

// Reference type arrays
String[] names;
Object[] objects;
Integer[] integers;
```

## Array Declaration and Creation

### Declaration Syntax

```java
// Preferred syntax
int[] numbers;
String[] names;

// Also valid (C-style)
int numbers[];
String names[];

// Multiple arrays
int[] arr1, arr2;  // Both are int arrays
int arr1[], arr2;  // arr1 is int[], arr2 is int
```

### Array Creation

```java
// Method 1: Declare then create
int[] numbers;
numbers = new int[5];  // Creates array of size 5, initialized to 0

// Method 2: Declare and create
int[] numbers = new int[5];

// Method 3: Declare, create, and initialize
int[] numbers = {1, 2, 3, 4, 5};

// Method 4: Anonymous array
int[] numbers = new int[]{1, 2, 3, 4, 5};
```

### Default Initialization

Arrays are automatically initialized with default values:

```java
int[] integers = new int[3];        // {0, 0, 0}
double[] doubles = new double[3];   // {0.0, 0.0, 0.0}
boolean[] booleans = new boolean[3]; // {false, false, false}
String[] strings = new String[3];   // {null, null, null}
Object[] objects = new Object[3];   // {null, null, null}
```

### Array Initialization Example

```java
// Primitive array
int[] scores = {95, 87, 92, 88, 91};

// Reference type array
String[] names = {"Alice", "Bob", "Charlie"};

// Mixed initialization
String[] words = new String[3];
words[0] = "Hello";
words[1] = "World";
words[2] = "Java";
```

## Array Operations

### Accessing Elements

```java
int[] numbers = {10, 20, 30, 40, 50};

// Reading
int first = numbers[0];   // 10
int last = numbers[4];    // 50

// Writing
numbers[2] = 35;  // {10, 20, 35, 40, 50}

// Length
int size = numbers.length;  // 5 (property, not method)
```

### ArrayIndexOutOfBoundsException

```java
int[] arr = {1, 2, 3};

int x = arr[3];   // Runtime error: ArrayIndexOutOfBoundsException
int y = arr[-1];  // Runtime error: ArrayIndexOutOfBoundsException

// Safe access
if (index >= 0 && index < arr.length) {
    int value = arr[index];
}
```

### Iterating Arrays

```java
int[] numbers = {1, 2, 3, 4, 5};

// Method 1: Traditional for loop
for (int i = 0; i < numbers.length; i++) {
    System.out.println(numbers[i]);
}

// Method 2: Enhanced for loop (for-each)
for (int num : numbers) {
    System.out.println(num);
}

// Method 3: Arrays.stream (Java 8+)
Arrays.stream(numbers).forEach(System.out::println);
```

### Modifying During Iteration

```java
int[] numbers = {1, 2, 3, 4, 5};

// Traditional loop allows modification
for (int i = 0; i < numbers.length; i++) {
    numbers[i] *= 2;  // Doubles each element
}
// {2, 4, 6, 8, 10}

// Enhanced for loop - CANNOT modify array structure
for (int num : numbers) {
    num *= 2;  // Only modifies local variable, not array
}
```

## Multi-Dimensional Arrays

### 2D Arrays

```java
// Declaration and creation
int[][] matrix = new int[3][4];  // 3 rows, 4 columns

// Initialization
int[][] matrix = {
    {1, 2, 3, 4},
    {5, 6, 7, 8},
    {9, 10, 11, 12}
};

// Accessing elements
int value = matrix[1][2];  // 7 (row 1, column 2)

// Iterating 2D array
for (int i = 0; i < matrix.length; i++) {
    for (int j = 0; j < matrix[i].length; j++) {
        System.out.print(matrix[i][j] + " ");
    }
    System.out.println();
}

// Enhanced for loop
for (int[] row : matrix) {
    for (int value : row) {
        System.out.print(value + " ");
    }
    System.out.println();
}
```

### Jagged Arrays

```java
// Asymmetric arrays (different row lengths)
int[][] jagged = {
    {1, 2},
    {3, 4, 5},
    {6, 7, 8, 9}
};

// Creating jagged array
int[][] jagged = new int[3][];
jagged[0] = new int[2];
jagged[1] = new int[3];
jagged[2] = new int[4];
```

### 3D Arrays

```java
// 3D array
int[][][] cube = new int[2][3][4];

// Initialization
int[][][] cube = {
    {{1, 2}, {3, 4}},
    {{5, 6}, {7, 8}}
};
```

## Arrays Class Utility Methods

The `java.util.Arrays` class provides static utility methods for array manipulation:

### Sorting

```java
import java.util.Arrays;

int[] numbers = {5, 2, 8, 1, 9};
Arrays.sort(numbers);  // {1, 2, 5, 8, 9}

// Sorting objects
String[] names = {"Charlie", "Alice", "Bob"};
Arrays.sort(names);  // {"Alice", "Bob", "Charlie"}

// Partial sort
int[] arr = {5, 3, 8, 1, 9, 2};
Arrays.sort(arr, 1, 4);  // Sort indices 1-3: {5, 1, 3, 8, 9, 2}
```

### Searching (Binary Search)

```java
int[] numbers = {1, 3, 5, 7, 9};  // Must be sorted

int index = Arrays.binarySearch(numbers, 5);  // Returns 2
int notFound = Arrays.binarySearch(numbers, 6);  // Returns negative value

// If not found, returns: -(insertion point) - 1
// insertion point = index where element would be inserted
```

### Copying

```java
int[] original = {1, 2, 3, 4, 5};

// Method 1: Arrays.copyOf
int[] copy1 = Arrays.copyOf(original, original.length);  // {1, 2, 3, 4, 5}
int[] larger = Arrays.copyOf(original, 7);  // {1, 2, 3, 4, 5, 0, 0}
int[] smaller = Arrays.copyOf(original, 3);  // {1, 2, 3}

// Method 2: Arrays.copyOfRange
int[] range = Arrays.copyOfRange(original, 1, 4);  // {2, 3, 4}

// Method 3: System.arraycopy
int[] dest = new int[5];
System.arraycopy(original, 0, dest, 0, 5);
```

### Comparing

```java
int[] arr1 = {1, 2, 3};
int[] arr2 = {1, 2, 3};
int[] arr3 = {1, 2, 4};

Arrays.equals(arr1, arr2);  // true
Arrays.equals(arr1, arr3);  // false

// Multi-dimensional comparison
int[][] matrix1 = {{1, 2}, {3, 4}};
int[][] matrix2 = {{1, 2}, {3, 4}};
Arrays.deepEquals(matrix1, matrix2);  // true
```

### Filling

```java
int[] arr = new int[5];
Arrays.fill(arr, 10);  // {10, 10, 10, 10, 10}

// Partial fill
Arrays.fill(arr, 1, 4, 20);  // {10, 20, 20, 20, 10}
```

### Converting to String

```java
int[] numbers = {1, 2, 3};
System.out.println(Arrays.toString(numbers));  // "[1, 2, 3]"

// Multi-dimensional
int[][] matrix = {{1, 2}, {3, 4}};
System.out.println(Arrays.deepToString(matrix));  // "[[1, 2], [3, 4]]"
```

## ArrayList Introduction

`ArrayList` is a **resizable array** implementation from the Collections Framework. Unlike arrays, ArrayLists can grow and shrink dynamically.

### Key Characteristics

- **Dynamic size**: Automatically grows/shrinks
- **Type-safe** (with generics): Stores specific type
- **Index-based access**: Like arrays
- **Allows duplicates**: Can store duplicate values
- **Maintains insertion order**: Elements stay in order added
- **Not synchronized**: Not thread-safe (use Collections.synchronizedList or Vector for thread-safety)

### Declaration and Creation

```java
import java.util.ArrayList;

// With generics (preferred)
ArrayList<String> names = new ArrayList<>();
ArrayList<Integer> numbers = new ArrayList<>();

// With initial capacity
ArrayList<String> largeList = new ArrayList<>(1000);

// From another collection
ArrayList<String> copy = new ArrayList<>(names);

// Without generics (legacy, not recommended)
ArrayList list = new ArrayList();  // Can store any Object
```

## ArrayList Operations

### Adding Elements

```java
ArrayList<String> list = new ArrayList<>();

// Add at end
list.add("Alice");   // ["Alice"]
list.add("Bob");     // ["Alice", "Bob"]

// Add at specific index
list.add(1, "Charlie");  // ["Alice", "Charlie", "Bob"]

// Add multiple
ArrayList<String> more = new ArrayList<>();
more.add("David");
more.add("Eve");
list.addAll(more);  // ["Alice", "Charlie", "Bob", "David", "Eve"]

// Add multiple at index
list.addAll(2, Arrays.asList("X", "Y"));
// ["Alice", "Charlie", "X", "Y", "Bob", "David", "Eve"]
```

### Accessing Elements

```java
ArrayList<String> list = new ArrayList<>(Arrays.asList("A", "B", "C"));

// Get element
String first = list.get(0);  // "A"
String last = list.get(list.size() - 1);  // "C"

// Size
int size = list.size();  // 3 (method, not property like array.length)

// Check if empty
boolean empty = list.isEmpty();  // false
```

### Modifying Elements

```java
ArrayList<Integer> numbers = new ArrayList<>(Arrays.asList(1, 2, 3, 4, 5));

// Set/replace element
numbers.set(2, 10);  // [1, 2, 10, 4, 5]

// Remove by index
numbers.remove(0);  // [2, 10, 4, 5] - removes first element

// Remove by object
numbers.remove(Integer.valueOf(10));  // [2, 4, 5]

// Remove all
numbers.removeAll(Arrays.asList(2, 4));  // [5]

// Clear all
numbers.clear();  // []
```

### Searching

```java
ArrayList<String> list = new ArrayList<>(Arrays.asList("A", "B", "C", "B"));

// Contains
boolean hasB = list.contains("B");  // true

// Index of first occurrence
int index = list.indexOf("B");  // 1

// Index of last occurrence
int lastIndex = list.lastIndexOf("B");  // 3

// Not found
int notFound = list.indexOf("Z");  // -1
```

### Iterating

```java
ArrayList<String> list = new ArrayList<>(Arrays.asList("A", "B", "C"));

// Enhanced for loop
for (String item : list) {
    System.out.println(item);
}

// Traditional for loop
for (int i = 0; i < list.size(); i++) {
    System.out.println(list.get(i));
}

// Iterator
Iterator<String> it = list.iterator();
while (it.hasNext()) {
    System.out.println(it.next());
}

// forEach (Java 8+)
list.forEach(System.out::println);
```

### Converting

```java
ArrayList<String> list = new ArrayList<>(Arrays.asList("A", "B", "C"));

// ArrayList to array
String[] array = list.toArray(new String[0]);

// ArrayList to array (sized)
String[] array2 = list.toArray(new String[list.size()]);

// Array to ArrayList
String[] arr = {"X", "Y", "Z"};
ArrayList<String> fromArray = new ArrayList<>(Arrays.asList(arr));
```

## ArrayList vs Array

| Feature | Array | ArrayList |
|---------|-------|-----------|
| Size | Fixed | Dynamic |
| Syntax | `int[]` | `ArrayList<Integer>` |
| Primitives | Supported | Not supported (use wrappers) |
| Length | `.length` (property) | `.size()` (method) |
| Type safety | Yes | Yes (with generics) |
| Performance | Faster for access | Slightly slower |
| Methods | Limited | Many utility methods |
| Flexibility | Low | High |

### When to Use

**Use Arrays when:**
- Size is known and fixed
- Need maximum performance
- Working with primitives
- Multi-dimensional data

**Use ArrayList when:**
- Size varies dynamically
- Need flexibility (add/remove)
- Prefer convenience methods
- Working with objects

## Best Practices

### 1. Specify Generic Type

```java
// BAD - raw type
ArrayList list = new ArrayList();

// GOOD - with generics
ArrayList<String> list = new ArrayList<>();
```

### 2. Initialize with Capacity for Large Lists

```java
// BAD - many resizes
ArrayList<String> large = new ArrayList<>();
for (int i = 0; i < 10000; i++) {
    large.add("Item" + i);
}

// GOOD - pre-sized
ArrayList<String> large = new ArrayList<>(10000);
for (int i = 0; i < 10000; i++) {
    large.add("Item" + i);
}
```

### 3. Use Enhanced For Loop for Read-Only

```java
// GOOD - clear and concise
for (String name : names) {
    System.out.println(name);
}
```

### 4. Check Bounds Before Accessing

```java
// BAD
String name = list.get(5);  // May throw IndexOutOfBoundsException

// GOOD
if (index >= 0 && index < list.size()) {
    String name = list.get(index);
}
```

### 5. Use toArray Correctly

```java
// BAD - type mismatch possible
Object[] arr = list.toArray();

// GOOD - type-safe
String[] arr = list.toArray(new String[0]);
```

## Summary

- **Arrays** are fixed-size, indexed containers of values
- Arrays are zero-indexed with `.length` property
- Multi-dimensional arrays can be symmetric or jagged
- `Arrays` class provides sort, search, copy, fill, equals, toString methods
- Binary search requires sorted array
- **ArrayList** is a dynamic, resizable array implementation
- ArrayList uses `.size()` method (not `.length` property)
- ArrayList provides add, remove, get, set, contains, indexOf methods
- ArrayList cannot store primitives directly (use wrapper classes)
- Arrays are faster but less flexible than ArrayList
- Use arrays for fixed-size, ArrayLists for dynamic collections

## Key Takeaways

1. Arrays have fixed size, ArrayList grows/shrinks dynamically
2. Arrays use `.length` property, ArrayList uses `.size()` method
3. Arrays can store primitives, ArrayList requires wrapper classes
4. `Arrays.sort()` sorts in-place, requires comparable elements
5. `Arrays.binarySearch()` requires sorted array
6. ArrayList add/remove operations may cause internal resizing
7. Multi-dimensional arrays are arrays of arrays
8. Always specify generic type for ArrayList (type safety)
9. Enhanced for loop cannot modify array structure
10. ArrayList provides rich API for manipulation compared to arrays
