# Module 10: Practice Questions - Standard Library

## Instructions
- Answer all 20 questions
- Score: Each correct answer = 5 points (Total: 100 points)
- **Passing score: 80/100 (16 correct answers)**

---

## Questions

### Question 1
What is the output?
```python
import math
print(math.ceil(4.2))
```
**A)** 5  
**B)** 4  
**C)** 4.2  
**D)** Error

---

### Question 2
What will be printed?
```python
import random
random.seed(0)
print(random.randint(1, 5))
random.seed(0)
print(random.randint(1, 5))
```
**A)** Same value both times  
**B)** Different values  
**C)** 0 0  
**D)** Error

---

### Question 3
What module is used for working with JSON?
**A)** json  
**B)** data  
**C)** serialization  
**D)** encoder

---

### Question 4
What is the output?
```python
from datetime import date
d = date(2024, 1, 15)
print(d.year)
```
**A)** 2024  
**B)** 1  
**C)** 15  
**D)** Error

---

### Question 5
What will be printed?
```python
from collections import Counter
c = Counter(['a', 'b', 'a', 'c', 'a'])
print(c['a'])
```
**A)** 3  
**B)** 1  
**C)** a  
**D)** Error

---

### Question 6
Which function returns current working directory?
**A)** os.getcwd()  
**B)** os.getdir()  
**C)** os.pwd()  
**D)** os.current()

---

### Question 7
What is the output?
```python
import math
print(math.floor(5.9))
```
**A)** 5  
**B)** 6  
**C)** 5.0  
**D)** Error

---

### Question 8
What will be printed?
```python
import sys
print(len(sys.argv) >= 1)
```
**A)** True  
**B)** False  
**C)** 1  
**D)** Error

---

### Question 9
What does json.loads() do?
**A)** Converts JSON string to Python object  
**B)** Converts Python object to JSON  
**C)** Loads JSON from file  
**D)** Saves JSON to file

---

### Question 10
What is the output?
```python
import random
numbers = [1, 2, 3]
print(type(random.choice(numbers)))
```
**A)** <class 'int'>  
**B)** <class 'list'>  
**C)** <class 'random'>  
**D)** Error

---

### Question 11
What will be printed?
```python
import math
print(math.sqrt(9))
```
**A)** 3.0  
**B)** 3  
**C)** 9  
**D)** Error

---

### Question 12
Which creates a named tuple?
**A)** collections.namedtuple  
**B)** tuple.named  
**C)** collections.tuple  
**D)** namedtuple()

---

### Question 13
What is the output?
```python
import os
path = os.path.join('folder', 'file.txt')
print('/' in path or '\\' in path)
```
**A)** True  
**B)** False  
**C)** Depends on OS  
**D)** Error

---

### Question 14
What will be printed?
```python
from datetime import timedelta
td = timedelta(days=7)
print(td.days)
```
**A)** 7  
**B)** 7.0  
**C)** timedelta(7)  
**D)** Error

---

### Question 15
What does random.shuffle() do?
**A)** Shuffles list in-place  
**B)** Returns shuffled copy  
**C)** Sorts list randomly  
**D)** Creates random list

---

### Question 16
What is the output?
```python
import math
print(math.factorial(0))
```
**A)** 1  
**B)** 0  
**C)** None  
**D)** Error

---

### Question 17
What will be printed?
```python
from collections import defaultdict
dd = defaultdict(int)
dd['x'] += 5
print(dd['x'])
```
**A)** 5  
**B)** 0  
**C)** KeyError  
**D)** Error

---

### Question 18
Which function converts Python object to JSON string?
**A)** json.dumps()  
**B)** json.loads()  
**C)** json.encode()  
**D)** json.stringify()

---

### Question 19
What is the output?
```python
import itertools
result = list(itertools.combinations([1, 2, 3], 2))
print(len(result))
```
**A)** 3  
**B)** 2  
**C)** 6  
**D)** Error

---

### Question 20
What will be printed?
```python
from datetime import datetime
dt = datetime(2024, 1, 15, 10, 30)
print(dt.hour)
```
**A)** 10  
**B)** 30  
**C)** 15  
**D)** Error

---

## Answers

### Answer 1: **A) 5**
**Explanation**: math.ceil() rounds up to nearest integer

---

### Answer 2: **A) Same value both times**
**Explanation**: Setting same seed produces same random sequence

---

### Answer 3: **A) json**
**Explanation**: json module handles JSON encoding/decoding

---

### Answer 4: **A) 2024**
**Explanation**: date.year attribute returns year value

---

### Answer 5: **A) 3**
**Explanation**: Counter counts occurrences; 'a' appears 3 times

---

### Answer 6: **A) os.getcwd()**
**Explanation**: getcwd() returns current working directory

---

### Answer 7: **A) 5**
**Explanation**: math.floor() rounds down to nearest integer

---

### Answer 8: **A) True**
**Explanation**: sys.argv always has at least one element (script name)

---

### Answer 9: **A) Converts JSON string to Python object**
**Explanation**: loads() deserializes JSON string to Python object

---

### Answer 10: **A) <class 'int'>**
**Explanation**: choice() returns one element from list (an integer)

---

### Answer 11: **A) 3.0**
**Explanation**: sqrt() returns float; square root of 9 is 3.0

---

### Answer 12: **A) collections.namedtuple**
**Explanation**: namedtuple is factory function in collections module

---

### Answer 13: **A) True**
**Explanation**: os.path.join() uses OS-appropriate path separator

---

### Answer 14: **A) 7**
**Explanation**: timedelta.days attribute returns number of days

---

### Answer 15: **A) Shuffles list in-place**
**Explanation**: shuffle() modifies original list, doesn't return new one

---

### Answer 16: **A) 1**
**Explanation**: 0! = 1 by mathematical definition

---

### Answer 17: **A) 5**
**Explanation**: defaultdict(int) creates default value 0; 0 + 5 = 5

---

### Answer 18: **A) json.dumps()**
**Explanation**: dumps() serializes Python object to JSON string

---

### Answer 19: **A) 3**
**Explanation**: combinations([1,2,3], 2) gives [(1,2), (1,3), (2,3)]

---

### Answer 20: **A) 10**
**Explanation**: datetime.hour attribute returns hour value

---

## Congratulations!

🎉 **You've completed all 10 modules of the Python PCAP Certification Study Guide!**

### What's Next?

1. **Review weak areas**: Go back to modules where you scored below 80%
2. **Practice coding**: Implement projects using concepts learned
3. **Take practice exams**: Use official PCAP practice tests
4. **Schedule exam**: Book your PCAP certification exam

### Study Resources
- Python Official Documentation: https://docs.python.org/3/
- PCAP Certification: https://pythoninstitute.org/pcap
- Practice on HackerRank, LeetCode, Codewars
- Build real projects to solidify understanding

**Good luck with your certification! 🐍**
