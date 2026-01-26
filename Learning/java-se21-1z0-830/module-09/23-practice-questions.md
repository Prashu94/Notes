# Module 9: Practice Questions - List and Set

## Questions (20)

---

### Question 1
```java
List<String> list = new ArrayList<>();
list.add("A");
list.add("B");
list.add("A");
System.out.println(list.size());
```

What is the output?

**A)** 2  
**B)** 3  
**C)** Compilation error  
**D)** Runtime exception

---

### Question 2
```java
List<Integer> numbers = Arrays.asList(1, 2, 3);
numbers.add(4);
System.out.println(numbers);
```

What happens when this code runs?

**A)** Prints [1, 2, 3, 4]  
**B)** Compilation error  
**C)** UnsupportedOperationException at runtime  
**D)** NullPointerException

---

### Question 3
```java
List<String> list = List.of("A", "B", "C");
list.set(0, "D");
```

What is the result?

**A)** list becomes ["D", "B", "C"]  
**B)** Compilation error  
**C)** UnsupportedOperationException at runtime  
**D)** IndexOutOfBoundsException

---

### Question 4
```java
List<String> list = new ArrayList<>();
list.add("Apple");
list.add(0, "Banana");
list.add("Cherry");
System.out.println(list);
```

What is the output?

**A)** [Apple, Banana, Cherry]  
**B)** [Banana, Apple, Cherry]  
**C)** [Banana, Cherry, Apple]  
**D)** Compilation error

---

### Question 5
```java
List<Integer> list = new ArrayList<>();
list.add(10);
list.add(20);
list.remove(1);
System.out.println(list);
```

What is printed?

**A)** [10]  
**B)** [20]  
**C)** [10, 20]  
**D)** []

---

### Question 6
```java
List<Integer> numbers = new ArrayList<>(List.of(10, 20, 30));
numbers.remove(Integer.valueOf(20));
System.out.println(numbers);
```

What is the output?

**A)** [10, 30]  
**B)** [10, 20]  
**C)** [20, 30]  
**D)** Compilation error

---

### Question 7
```java
Set<String> set = new HashSet<>();
set.add("Apple");
set.add("Banana");
set.add("Apple");
System.out.println(set.size());
```

What is printed?

**A)** 1  
**B)** 2  
**C)** 3  
**D)** Compilation error

---

### Question 8
```java
Set<Integer> set = new TreeSet<>();
set.add(5);
set.add(1);
set.add(3);
System.out.println(set);
```

What is the output?

**A)** [5, 1, 3]  
**B)** [1, 3, 5]  
**C)** [3, 1, 5]  
**D)** Order is unpredictable

---

### Question 9
```java
Set<String> set = new LinkedHashSet<>();
set.add("Z");
set.add("A");
set.add("M");
System.out.println(set);
```

What is printed?

**A)** [A, M, Z]  
**B)** [Z, A, M]  
**C)** [M, A, Z]  
**D)** Order is unpredictable

---

### Question 10
```java
List<String> list = new LinkedList<>();
((LinkedList<String>) list).addFirst("A");
list.add("B");
((LinkedList<String>) list).addLast("C");
System.out.println(list);
```

What is the output?

**A)** [A, B, C]  
**B)** [C, B, A]  
**C)** [B, A, C]  
**D)** Compilation error

---

### Question 11
```java
Set<String> set1 = new HashSet<>(Set.of("A", "B", "C"));
Set<String> set2 = new HashSet<>(Set.of("B", "C", "D"));
set1.retainAll(set2);
System.out.println(set1);
```

What is printed?

**A)** [A, B, C, D]  
**B)** [B, C]  
**C)** [A]  
**D)** [D]

---

### Question 12
```java
List<String> list = new ArrayList<>(List.of("A", "B", "C"));
Collections.reverse(list);
System.out.println(list);
```

What is the output?

**A)** [A, B, C]  
**B)** [C, B, A]  
**C)** Compilation error  
**D)** Runtime exception

---

### Question 13
```java
Set<Integer> set = new TreeSet<>();
set.add(null);
System.out.println(set);
```

What happens?

**A)** Prints [null]  
**B)** Prints []  
**C)** NullPointerException at runtime  
**D)** Compilation error

---

### Question 14
```java
List<String> list = new ArrayList<>();
list.add("A");
list.add("B");
String result = list.get(2);
```

What is the result?

**A)** result is null  
**B)** result is "B"  
**C)** IndexOutOfBoundsException at runtime  
**D)** Compilation error

---

### Question 15
```java
Set<String> set = Set.of("A", "B", "C");
set.add("D");
```

What happens?

**A)** set becomes {A, B, C, D}  
**B)** Compilation error  
**C)** UnsupportedOperationException at runtime  
**D)** NullPointerException

---

### Question 16
```java
List<Integer> list = new ArrayList<>();
list.add(1);
list.add(2);
list.add(3);
list.remove(1);
System.out.println(list);
```

What is printed?

**A)** [1, 3]  
**B)** [2, 3]  
**C)** [1, 2]  
**D)** [3]

---

### Question 17
```java
NavigableSet<Integer> set = new TreeSet<>(Set.of(1, 3, 5, 7, 9));
Integer result = set.ceiling(6);
System.out.println(result);
```

What is the output?

**A)** 5  
**B)** 6  
**C)** 7  
**D)** null

---

### Question 18
```java
List<String> list = new ArrayList<>();
for (int i = 0; i < 3; i++) {
    list.add("Item");
}
System.out.println(list.size());
```

What is printed?

**A)** 0  
**B)** 1  
**C)** 3  
**D)** Compilation error

---

### Question 19
```java
Set<String> set1 = new HashSet<>(Set.of("A", "B"));
Set<String> set2 = new HashSet<>(Set.of("C", "D"));
set1.addAll(set2);
System.out.println(set1.size());
```

What is the output?

**A)** 2  
**B)** 4  
**C)** 6  
**D)** Compilation error

---

### Question 20
```java
List<Integer> numbers = new ArrayList<>(List.of(3, 1, 4, 1, 5));
Set<Integer> unique = new HashSet<>(numbers);
System.out.println(unique.size());
```

What is printed?

**A)** 4  
**B)** 5  
**C)** 3  
**D)** Compilation error

---

## Answers and Explanations

### Answer 1: **B)** 3

**Explanation:**  
`ArrayList` allows duplicate elements. The list contains three elements: "A", "B", "A".

```java
List<String> list = new ArrayList<>();
list.add("A");      // [A]
list.add("B");      // [A, B]
list.add("A");      // [A, B, A] - duplicate allowed
System.out.println(list.size()); // 3
```

---

### Answer 2: **C)** UnsupportedOperationException at runtime

**Explanation:**  
`Arrays.asList()` returns a **fixed-size list** backed by the original array. You cannot add or remove elements.

```java
List<Integer> numbers = Arrays.asList(1, 2, 3); // Fixed size
// numbers.add(4); // UnsupportedOperationException!

// To create a mutable list:
List<Integer> mutable = new ArrayList<>(Arrays.asList(1, 2, 3));
mutable.add(4); // Works
```

---

### Answer 3: **C)** UnsupportedOperationException at runtime

**Explanation:**  
`List.of()` creates an **immutable list**. Any modification operation throws `UnsupportedOperationException`.

```java
List<String> immutable = List.of("A", "B", "C");
// immutable.set(0, "D");    // UnsupportedOperationException
// immutable.add("D");       // UnsupportedOperationException
// immutable.remove(0);      // UnsupportedOperationException

// To create mutable:
List<String> mutable = new ArrayList<>(List.of("A", "B", "C"));
mutable.set(0, "D"); // Works
```

---

### Answer 4: **B)** [Banana, Apple, Cherry]

**Explanation:**  
`add(index, element)` inserts at the specified index, shifting existing elements to the right.

```java
List<String> list = new ArrayList<>();
list.add("Apple");        // [Apple]
list.add(0, "Banana");    // [Banana, Apple] - insert at index 0
list.add("Cherry");       // [Banana, Apple, Cherry] - add at end
```

---

### Answer 5: **A)** [10]

**Explanation:**  
`remove(index)` removes the element at the specified index (1), which is 20.

```java
List<Integer> list = new ArrayList<>();
list.add(10);       // [10]
list.add(20);       // [10, 20]
list.remove(1);     // [10] - removes element at index 1 (20)
```

---

### Answer 6: **A)** [10, 30]

**Explanation:**  
`remove(Object)` removes the first occurrence of the specified object. `Integer.valueOf(20)` creates an Integer object.

```java
List<Integer> numbers = new ArrayList<>(List.of(10, 20, 30));
// numbers.remove(20);  // Would remove element at index 20!
numbers.remove(Integer.valueOf(20)); // Removes object 20
// Result: [10, 30]

// Note: remove(int) removes by index, remove(Object) removes by value
```

---

### Answer 7: **B)** 2

**Explanation:**  
`HashSet` does **not allow duplicates**. The second "Apple" is not added.

```java
Set<String> set = new HashSet<>();
set.add("Apple");   // Added
set.add("Banana");  // Added
set.add("Apple");   // Not added - duplicate
System.out.println(set.size()); // 2
```

---

### Answer 8: **B)** [1, 3, 5]

**Explanation:**  
`TreeSet` maintains elements in **sorted (natural) order**.

```java
Set<Integer> set = new TreeSet<>();
set.add(5);  // [5]
set.add(1);  // [1, 5]
set.add(3);  // [1, 3, 5] - sorted order
```

---

### Answer 9: **B)** [Z, A, M]

**Explanation:**  
`LinkedHashSet` maintains **insertion order**.

```java
Set<String> set = new LinkedHashSet<>();
set.add("Z");  // [Z]
set.add("A");  // [Z, A]
set.add("M");  // [Z, A, M] - insertion order
```

---

### Answer 10: **A)** [A, B, C]

**Explanation:**  
`LinkedList` provides `addFirst()` and `addLast()` methods.

```java
List<String> list = new LinkedList<>();
((LinkedList<String>) list).addFirst("A");  // [A]
list.add("B");                              // [A, B]
((LinkedList<String>) list).addLast("C");   // [A, B, C]
```

---

### Answer 11: **B)** [B, C]

**Explanation:**  
`retainAll()` retains only elements that are in **both** sets (intersection).

```java
Set<String> set1 = new HashSet<>(Set.of("A", "B", "C"));
Set<String> set2 = new HashSet<>(Set.of("B", "C", "D"));
set1.retainAll(set2); // Intersection: [B, C]
```

---

### Answer 12: **B)** [C, B, A]

**Explanation:**  
`Collections.reverse()` reverses the order of elements in the list.

```java
List<String> list = new ArrayList<>(List.of("A", "B", "C"));
Collections.reverse(list);  // [C, B, A]
```

---

### Answer 13: **C)** NullPointerException at runtime

**Explanation:**  
`TreeSet` does **not allow null** elements because it needs to compare elements.

```java
Set<Integer> set = new TreeSet<>();
// set.add(null); // NullPointerException!

// HashSet and LinkedHashSet allow one null
Set<Integer> hashSet = new HashSet<>();
hashSet.add(null); // OK
```

---

### Answer 14: **C)** IndexOutOfBoundsException at runtime

**Explanation:**  
The list has only 2 elements (indices 0 and 1). Accessing index 2 throws `IndexOutOfBoundsException`.

```java
List<String> list = new ArrayList<>();
list.add("A");  // index 0
list.add("B");  // index 1
// String result = list.get(2); // IndexOutOfBoundsException!
```

---

### Answer 15: **C)** UnsupportedOperationException at runtime

**Explanation:**  
`Set.of()` creates an **immutable set**. Modification operations throw `UnsupportedOperationException`.

```java
Set<String> immutable = Set.of("A", "B", "C");
// immutable.add("D"); // UnsupportedOperationException!

Set<String> mutable = new HashSet<>(Set.of("A", "B", "C"));
mutable.add("D"); // Works
```

---

### Answer 16: **A)** [1, 3]

**Explanation:**  
`remove(1)` removes the element at **index 1**, which is 2.

```java
List<Integer> list = new ArrayList<>();
list.add(1);     // [1]
list.add(2);     // [1, 2]
list.add(3);     // [1, 2, 3]
list.remove(1);  // [1, 3] - removes element at index 1 (which is 2)
```

---

### Answer 17: **C)** 7

**Explanation:**  
`ceiling(6)` returns the **smallest element >= 6**, which is 7.

```java
NavigableSet<Integer> set = new TreeSet<>(Set.of(1, 3, 5, 7, 9));
// ceiling(6) -> 7 (smallest >= 6)
// floor(6) -> 5 (largest <= 6)
// higher(6) -> 7 (smallest > 6)
// lower(6) -> 5 (largest < 6)
```

---

### Answer 18: **C)** 3

**Explanation:**  
The loop runs 3 times, adding "Item" each time.

```java
List<String> list = new ArrayList<>();
for (int i = 0; i < 3; i++) {
    list.add("Item");
}
// list = [Item, Item, Item]
System.out.println(list.size()); // 3
```

---

### Answer 19: **B)** 4

**Explanation:**  
`addAll()` adds all elements from set2 to set1 (union).

```java
Set<String> set1 = new HashSet<>(Set.of("A", "B"));
Set<String> set2 = new HashSet<>(Set.of("C", "D"));
set1.addAll(set2); // set1 = {A, B, C, D}
System.out.println(set1.size()); // 4
```

---

### Answer 20: **A)** 4

**Explanation:**  
The list has 5 elements, but one is a duplicate (1 appears twice). The set contains only unique elements: 3, 1, 4, 5.

```java
List<Integer> numbers = new ArrayList<>(List.of(3, 1, 4, 1, 5));
// List: [3, 1, 4, 1, 5] - 5 elements
Set<Integer> unique = new HashSet<>(numbers);
// Set: {1, 3, 4, 5} - 4 unique elements
```

---

## Score Interpretation

- **18-20 correct**: Excellent! You have mastered List and Set collections.
- **15-17 correct**: Good understanding. Review the topics you missed.
- **12-14 correct**: Fair. Study the theory again and practice more.
- **Below 12**: Need more practice. Review all concepts thoroughly.

---

**Previous:** [Theory - List and Set](23-list-set.md)  
**Next:** [Theory - Map and Deque](24-map-deque.md)
