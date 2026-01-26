# Module 5 Part 2: Practice Questions - Lambda and Functional Programming

## Instructions
- Answer all 20 questions
- Score: Each correct answer = 5 points (Total: 100 points)
- **Passing score: 80/100 (16 correct answers)**

---

## Questions

### Question 1
What is the output?
```python
square = lambda x: x ** 2
print(square(5))
```
**A)** 25  
**B)** 10  
**C)** 5  
**D)** Error

---

### Question 2
What will be printed?
```python
add = lambda a, b: a + b
print(add(3, 4))
```
**A)** 7  
**B)** 34  
**C)** (3, 4)  
**D)** Error

---

### Question 3
What is the output?
```python
nums = [1, 2, 3, 4]
result = list(map(lambda x: x * 2, nums))
print(result)
```
**A)** [2, 4, 6, 8]  
**B)** [1, 2, 3, 4]  
**C)** 20  
**D)** Error

---

### Question 4
What will be printed?
```python
nums = [1, 2, 3, 4, 5, 6]
result = list(filter(lambda x: x % 2 == 0, nums))
print(result)
```
**A)** [2, 4, 6]  
**B)** [1, 3, 5]  
**C)** [1, 2, 3, 4, 5, 6]  
**D)** Error

---

### Question 5
What is the output?
```python
from functools import reduce
nums = [1, 2, 3, 4]
result = reduce(lambda x, y: x + y, nums)
print(result)
```
**A)** 10  
**B)** [1, 2, 3, 4]  
**C)** 24  
**D)** Error

---

### Question 6
What will be printed?
```python
func = lambda: "Hello"
print(func())
```
**A)** Hello  
**B)** lambda  
**C)** None  
**D)** Error

---

### Question 7
What is the output?
```python
nums = [1, 2, 3]
result = list(map(lambda x: x ** 2, nums))
print(len(result))
```
**A)** 3  
**B)** 14  
**C)** 6  
**D)** Error

---

### Question 8
What will be printed?
```python
words = ["", "hello", "", "world"]
result = list(filter(None, words))
print(len(result))
```
**A)** 2  
**B)** 4  
**C)** 0  
**D)** Error

---

### Question 9
What is the output?
```python
nums = [3, 1, 4, 1, 5, 9, 2, 6]
result = sorted(nums, key=lambda x: -x)
print(result[0])
```
**A)** 9  
**B)** 1  
**C)** 6  
**D)** 3

---

### Question 10
What will be printed?
```python
from functools import reduce
nums = [1, 2, 3]
result = reduce(lambda x, y: x * y, nums)
print(result)
```
**A)** 6  
**B)** 123  
**C)** 9  
**D)** Error

---

### Question 11
What is the output?
```python
pairs = [(1, 'a'), (3, 'c'), (2, 'b')]
result = sorted(pairs, key=lambda x: x[0])
print(result[0])
```
**A)** (1, 'a')  
**B)** 1  
**C)** 'a'  
**D)** Error

---

### Question 12
What will be printed?
```python
multiply = lambda x, y=2: x * y
print(multiply(5))
```
**A)** 10  
**B)** 5  
**C)** 7  
**D)** Error

---

### Question 13
What is the output?
```python
nums = [1, 2, 3, 4, 5]
result = list(map(lambda x: x if x % 2 == 0 else 0, nums))
print(result)
```
**A)** [0, 2, 0, 4, 0]  
**B)** [2, 4]  
**C)** [1, 3, 5]  
**D)** Error

---

### Question 14
What will be printed?
```python
nums = [1, 2, 3]
result = list(filter(lambda x: x > 1, nums))
print(len(result))
```
**A)** 2  
**B)** 3  
**C)** 1  
**D)** 0

---

### Question 15
What is the output?
```python
from functools import reduce
nums = [5]
result = reduce(lambda x, y: x + y, nums)
print(result)
```
**A)** 5  
**B)** [5]  
**C)** 0  
**D)** Error

---

### Question 16
What will be printed?
```python
words = ["apple", "Banana", "cherry"]
result = sorted(words, key=lambda s: s.lower())
print(result[0])
```
**A)** apple  
**B)** Banana  
**C)** cherry  
**D)** Error

---

### Question 17
What is the output?
```python
def make_adder(n):
    return lambda x: x + n

add_10 = make_adder(10)
print(add_10(5))
```
**A)** 15  
**B)** 10  
**C)** 5  
**D)** Error

---

### Question 18
What will be printed?
```python
nums = [1, 2, 3, 4]
result = list(map(lambda x: x + 1, filter(lambda x: x % 2 == 0, nums)))
print(result)
```
**A)** [3, 5]  
**B)** [2, 4]  
**C)** [2, 3, 4, 5]  
**D)** Error

---

### Question 19
What is the output?
```python
from functools import reduce
nums = [1, 2, 3, 4]
result = reduce(lambda x, y: x + y, nums, 10)
print(result)
```
**A)** 20  
**B)** 10  
**C)** 14  
**D)** Error

---

### Question 20
What will be printed?
```python
f = lambda x, y, z: x + y + z
print(f(1, 2, 3))
```
**A)** 6  
**B)** 123  
**C)** (1, 2, 3)  
**D)** Error

---

## Answers

### Answer 1: **A) 25**
**Explanation**: Lambda squares 5: 5² = 25

---

### Answer 2: **A) 7**
**Explanation**: Lambda adds 3 + 4 = 7

---

### Answer 3: **A) [2, 4, 6, 8]**
**Explanation**: map() doubles each element

---

### Answer 4: **A) [2, 4, 6]**
**Explanation**: filter() keeps even numbers only

---

### Answer 5: **A) 10**
**Explanation**: reduce() sums: ((1+2)+3)+4 = 10

---

### Answer 6: **A) Hello**
**Explanation**: Lambda with no parameters returns "Hello"

---

### Answer 7: **A) 3**
**Explanation**: map() creates list of 3 squared values

---

### Answer 8: **A) 2**
**Explanation**: filter(None) removes falsy values (empty strings)

---

### Answer 9: **A) 9**
**Explanation**: Sorted descending by -x, largest first

---

### Answer 10: **A) 6**
**Explanation**: reduce() multiplies: (1*2)*3 = 6

---

### Answer 11: **A) (1, 'a')**
**Explanation**: Sorted by first element, (1,'a') is first

---

### Answer 12: **A) 10**
**Explanation**: Default y=2, so 5 * 2 = 10

---

### Answer 13: **A) [0, 2, 0, 4, 0]**
**Explanation**: map() keeps even numbers, replaces odd with 0

---

### Answer 14: **A) 2**
**Explanation**: filter() keeps values > 1, that's [2, 3]

---

### Answer 15: **A) 5**
**Explanation**: Single element, reduce returns it

---

### Answer 16: **A) apple**
**Explanation**: Case-insensitive sort, "apple" first alphabetically

---

### Answer 17: **A) 15**
**Explanation**: Closure remembers n=10, returns 5 + 10 = 15

---

### Answer 18: **A) [3, 5]**
**Explanation**: Filter evens [2,4], map adds 1: [3,5]

---

### Answer 19: **A) 20**
**Explanation**: Initial value 10 + sum(1+2+3+4) = 20

---

### Answer 20: **A) 6**
**Explanation**: Lambda adds three parameters: 1 + 2 + 3 = 6

---

## Next Steps
✅ **If you scored 80+**: Proceed to **Module 6: Modules**  
❌ **If you scored below 80**: Review lambda and functional programming
