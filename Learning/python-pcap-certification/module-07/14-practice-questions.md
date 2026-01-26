# Module 7: Practice Questions - File Operations

## Instructions
- Answer all 20 questions
- Score: Each correct answer = 5 points (Total: 100 points)
- **Passing score: 80/100 (16 correct answers)**

---

## Questions

### Question 1
What is the default file mode if not specified?
```python
file = open('data.txt')
```
**A)** 'r' (read)  
**B)** 'w' (write)  
**C)** 'a' (append)  
**D)** 'r+' (read/write)

---

### Question 2
What happens when you open a file in 'w' mode and file exists?
**A)** File content is erased  
**B)** Content is appended  
**C)** Error is raised  
**D)** File is opened read-only

---

### Question 3
What is the output?
```python
with open('test.txt', 'w') as f:
    f.write('Hello')
    f.write('World')
```
**A)** File contains: HelloWorld  
**B)** File contains: Hello World  
**C)** File contains: Hello\nWorld  
**D)** Error

---

### Question 4
What method reads one line from a file?
**A)** readline()  
**B)** read()  
**C)** readlines()  
**D)** getline()

---

### Question 5
What is the output?
```python
lines = ['A\n', 'B\n', 'C\n']
with open('test.txt', 'w') as f:
    f.writelines(lines)
# How many lines in file?
```
**A)** 3  
**B)** 1  
**C)** 0  
**D)** Error

---

### Question 6
What does this return?
```python
with open('test.txt', 'r') as f:
    result = f.readable()
print(result)
```
**A)** True  
**B)** False  
**C)** 'r'  
**D)** None

---

### Question 7
What is the benefit of using `with` statement?
**A)** Automatically closes file  
**B)** Faster file operations  
**C)** Encrypts file content  
**D)** Compresses file

---

### Question 8
What will be printed?
```python
with open('test.txt', 'w') as f:
    f.write('Hello')
    print(f.tell())
```
**A)** 5  
**B)** 0  
**C)** 1  
**D)** Error

---

### Question 9
What does `seek(0)` do?
**A)** Moves to beginning of file  
**B)** Moves to end of file  
**C)** Closes file  
**D)** Deletes file

---

### Question 10
What is the output?
```python
# test.txt contains: "Hello\nWorld\n"
with open('test.txt', 'r') as f:
    line = f.readline()
    print(len(line))
```
**A)** 6 (Hello\n)  
**B)** 5 (Hello)  
**C)** 12 (entire file)  
**D)** Error

---

### Question 11
Which mode creates file if it doesn't exist?
**A)** 'w'  
**B)** 'r'  
**C)** 'r+'  
**D)** Both A and C

---

### Question 12
What is the output?
```python
with open('test.txt', 'w') as f:
    print('Hello', 'World', file=f)
# What's in the file?
```
**A)** Hello World\n  
**B)** HelloWorld  
**C)** Hello,World  
**D)** Error

---

### Question 13
What exception is raised if file doesn't exist in read mode?
```python
with open('missing.txt', 'r') as f:
    content = f.read()
```
**A)** FileNotFoundError  
**B)** IOError  
**C)** ValueError  
**D)** OSError

---

### Question 14
What does this return?
```python
# test.txt contains: "ABC"
with open('test.txt', 'r') as f:
    f.read(2)
    position = f.tell()
print(position)
```
**A)** 2  
**B)** 1  
**C)** 3  
**D)** 0

---

### Question 15
Which mode appends without overwriting?
**A)** 'a'  
**B)** 'w'  
**C)** 'r+'  
**D)** 'w+'

---

### Question 16
What is the output?
```python
# test.txt contains: "Line1\nLine2\nLine3\n"
with open('test.txt', 'r') as f:
    lines = f.readlines()
    print(len(lines))
```
**A)** 3  
**B)** 1  
**C)** 4  
**D)** Error

---

### Question 17
What does 'rb' mode indicate?
**A)** Read binary  
**B)** Read buffer  
**C)** Read both  
**D)** Read block

---

### Question 18
What will be printed?
```python
with open('test.txt', 'w') as f:
    f.write('Test')
    closed_status = f.closed
print(closed_status)
```
**A)** False  
**B)** True  
**C)** None  
**D)** Error

---

### Question 19
What is most memory-efficient for large files?
```python
# test.txt is 10GB
```
**A)** `for line in file:`  
**B)** `file.read()`  
**C)** `file.readlines()`  
**D)** `file.read().split('\n')`

---

### Question 20
What will be printed?
```python
with open('test.txt', 'w') as f:
    pass  # Do nothing
# After with block
print(f.closed)
```
**A)** True  
**B)** False  
**C)** None  
**D)** Error

---

## Answers

### Answer 1: **A) 'r' (read)**
**Explanation**: Default mode is read ('r') if not specified

---

### Answer 2: **A) File content is erased**
**Explanation**: Write mode ('w') truncates (erases) existing file

---

### Answer 3: **A) File contains: HelloWorld**
**Explanation**: write() doesn't add newlines automatically; output is concatenated

---

### Answer 4: **A) readline()**
**Explanation**: readline() reads one line from file

---

### Answer 5: **A) 3**
**Explanation**: writelines() writes each string in list as separate line

---

### Answer 6: **A) True**
**Explanation**: readable() returns True for files opened in read mode

---

### Answer 7: **A) Automatically closes file**
**Explanation**: `with` statement ensures file is closed even if exception occurs

---

### Answer 8: **A) 5**
**Explanation**: tell() returns current position; 'Hello' is 5 characters

---

### Answer 9: **A) Moves to beginning of file**
**Explanation**: seek(0) sets file position to start

---

### Answer 10: **A) 6 (Hello\n)**
**Explanation**: readline() reads entire line including newline character

---

### Answer 11: **A) 'w'**
**Explanation**: Write mode creates file if it doesn't exist; 'r+' requires existing file

---

### Answer 12: **A) Hello World\n**
**Explanation**: print() adds space between arguments and newline at end

---

### Answer 13: **A) FileNotFoundError**
**Explanation**: Opening non-existent file in read mode raises FileNotFoundError

---

### Answer 14: **A) 2**
**Explanation**: After reading 2 characters, position is at index 2

---

### Answer 15: **A) 'a'**
**Explanation**: Append mode ('a') adds to end without erasing existing content

---

### Answer 16: **A) 3**
**Explanation**: readlines() returns list with 3 elements (one per line)

---

### Answer 17: **A) Read binary**
**Explanation**: 'rb' means read in binary mode

---

### Answer 18: **A) False**
**Explanation**: Inside `with` block, file is still open; closed is False

---

### Answer 19: **A) `for line in file:`**
**Explanation**: Iterating over file object reads one line at a time (memory efficient)

---

### Answer 20: **A) True**
**Explanation**: After `with` block exits, file is automatically closed

---

## Next Steps
✅ **If you scored 80+**: Proceed to **Module 8: Exception Handling**  
❌ **If you scored below 80**: Review file operations theory and practice more
