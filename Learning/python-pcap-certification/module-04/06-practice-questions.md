# Module 4 Part 1: Practice Questions - Lists

## Instructions
- Answer all 20 questions
- Score: Each correct answer = 5 points (Total: 100 points)
- **Passing score: 80/100 (16 correct answers)**

---

## Questions

### Question 1
What is the output?
```python
nums = [1, 2, 3]
nums.append(4)
print(nums)
```
**A)** [1, 2, 3, 4]  
**B)** [1, 2, 3, [4]]  
**C)** [4, 1, 2, 3]  
**D)** Error

---

### Question 2
What will be printed?
```python
nums = [1, 2, 3]
nums.extend([4, 5])
print(nums)
```
**A)** [1, 2, 3, 4, 5]  
**B)** [1, 2, 3, [4, 5]]  
**C)** [[1, 2, 3], [4, 5]]  
**D)** Error

---

### Question 3
What is the output?
```python
nums = [1, 2, 3, 4, 5]
print(nums[1:4])
```
**A)** [1, 2, 3, 4]  
**B)** [2, 3, 4]  
**C)** [2, 3, 4, 5]  
**D)** [1, 2, 3]

---

### Question 4
What will be printed?
```python
nums = [1, 2, 3, 4, 5]
print(nums[-1])
```
**A)** 1  
**B)** 5  
**C)** -1  
**D)** Error

---

### Question 5
What is the output?
```python
nums = [3, 1, 4, 1, 5]
nums.sort()
print(nums)
```
**A)** [3, 1, 4, 1, 5]  
**B)** [1, 1, 3, 4, 5]  
**C)** [5, 4, 3, 1, 1]  
**D)** None

---

### Question 6
What will be printed?
```python
nums = [1, 2, 3, 2, 4]
print(nums.count(2))
```
**A)** 1  
**B)** 2  
**C)** 3  
**D)** 4

---

### Question 7
What is the output?
```python
nums = [1, 2, 3]
result = nums.pop()
print(result)
```
**A)** [1, 2]  
**B)** 3  
**C)** [1, 2, 3]  
**D)** None

---

### Question 8
What will be printed?
```python
nums = [1, 2, 3, 4, 5]
print(nums[::2])
```
**A)** [1, 2, 3, 4, 5]  
**B)** [1, 3, 5]  
**C)** [2, 4]  
**D)** [5, 3, 1]

---

### Question 9
What is the output?
```python
nums = [1, 2, 3]
nums.insert(1, 99)
print(nums)
```
**A)** [1, 99, 2, 3]  
**B)** [99, 1, 2, 3]  
**C)** [1, 2, 99, 3]  
**D)** [1, 2, 3, 99]

---

### Question 10
What will be printed?
```python
nums = [x**2 for x in range(4)]
print(nums)
```
**A)** [0, 1, 4, 9]  
**B)** [1, 4, 9, 16]  
**C)** [0, 1, 2, 3]  
**D)** SyntaxError

---

### Question 11
What is the output?
```python
nums = [1, 2, 3]
nums2 = nums
nums2.append(4)
print(nums)
```
**A)** [1, 2, 3]  
**B)** [1, 2, 3, 4]  
**C)** [4]  
**D)** Error

---

### Question 12
What will be printed?
```python
nums = [1, 2, 3, 4, 5]
print(nums[::-1])
```
**A)** [1, 2, 3, 4, 5]  
**B)** [5, 4, 3, 2, 1]  
**C)** [2, 3, 4, 5]  
**D)** Error

---

### Question 13
What is the output?
```python
nums = [1, 2, 3]
nums.remove(2)
print(nums)
```
**A)** [1, 3]  
**B)** [1, 2, 3]  
**C)** [2]  
**D)** None

---

### Question 14
What will be printed?
```python
nums = [1, 2, 3]
print(len(nums))
```
**A)** 2  
**B)** 3  
**C)** 4  
**D)** Error

---

### Question 15
What is the output?
```python
nums = [1, 2, 3, 4, 5]
print(nums[-3:])
```
**A)** [1, 2, 3]  
**B)** [3, 4, 5]  
**C)** [4, 5]  
**D)** [5]

---

### Question 16
What will be printed?
```python
nums = [1, 2, 3]
nums.clear()
print(nums)
```
**A)** [1, 2, 3]  
**B)** []  
**C)** None  
**D)** Error

---

### Question 17
What is the output?
```python
nums = [1, 2, 3] * 2
print(nums)
```
**A)** [2, 4, 6]  
**B)** [1, 2, 3, 1, 2, 3]  
**C)** [[1, 2, 3], [1, 2, 3]]  
**D)** Error

---

### Question 18
What will be printed?
```python
nums = [5, 2, 8, 1, 9]
print(max(nums))
```
**A)** 5  
**B)** 9  
**C)** 1  
**D)** Error

---

### Question 19
What is the output?
```python
nums = [1, 2, 3]
nums.reverse()
print(nums)
```
**A)** [1, 2, 3]  
**B)** [3, 2, 1]  
**C)** None  
**D)** Error

---

### Question 20
What will be printed?
```python
nums = [x for x in range(5) if x % 2 == 0]
print(nums)
```
**A)** [0, 2, 4]  
**B)** [1, 3]  
**C)** [0, 1, 2, 3, 4]  
**D)** [2, 4]

---

## Answers

### Answer 1: **A) [1, 2, 3, 4]**
**Explanation**: `append()` adds single element to end

---

### Answer 2: **A) [1, 2, 3, 4, 5]**
**Explanation**: `extend()` adds multiple elements

---

### Answer 3: **B) [2, 3, 4]**
**Explanation**: Slice from index 1 to 4 (exclusive)

---

### Answer 4: **B) 5**
**Explanation**: Negative index -1 refers to last element

---

### Answer 5: **B) [1, 1, 3, 4, 5]**
**Explanation**: `sort()` sorts in-place, ascending order

---

### Answer 6: **B) 2**
**Explanation**: `count()` returns number of occurrences (2 appears twice)

---

### Answer 7: **B) 3**
**Explanation**: `pop()` removes and returns last element

---

### Answer 8: **B) [1, 3, 5]**
**Explanation**: Slice with step 2, every second element starting from index 0

---

### Answer 9: **A) [1, 99, 2, 3]**
**Explanation**: `insert(1, 99)` inserts 99 at index 1

---

### Answer 10: **A) [0, 1, 4, 9]**
**Explanation**: List comprehension: squares of 0, 1, 2, 3

---

### Answer 11: **B) [1, 2, 3, 4]**
**Explanation**: `nums2` is a reference to `nums`, not a copy. Both modified

---

### Answer 12: **B) [5, 4, 3, 2, 1]**
**Explanation**: Slice with step -1 reverses the list

---

### Answer 13: **A) [1, 3]**
**Explanation**: `remove()` removes first occurrence of value

---

### Answer 14: **B) 3**
**Explanation**: `len()` returns number of elements

---

### Answer 15: **B) [3, 4, 5]**
**Explanation**: Negative slice `[-3:]` gets last 3 elements

---

### Answer 16: **B) []**
**Explanation**: `clear()` removes all elements

---

### Answer 17: **B) [1, 2, 3, 1, 2, 3]**
**Explanation**: List repetition creates concatenated copy

---

### Answer 18: **B) 9**
**Explanation**: `max()` returns largest element

---

### Answer 19: **B) [3, 2, 1]**
**Explanation**: `reverse()` reverses list in-place

---

### Answer 20: **A) [0, 2, 4]**
**Explanation**: List comprehension with condition, even numbers only

---

## Next Steps
✅ **If you scored 80+**: Proceed to **Module 4: Tuples**  
❌ **If you scored below 80**: Review lists theory and practice more
