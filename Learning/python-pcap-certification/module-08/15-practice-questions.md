# Module 8: Practice Questions - Exception Handling

## Instructions
- Answer all 20 questions
- Score: Each correct answer = 5 points (Total: 100 points)
- **Passing score: 80/100 (16 correct answers)**

---

## Questions

### Question 1
What is the output?
```python
try:
    print(10 / 0)
except ZeroDivisionError:
    print("Error")
```
**A)** Error  
**B)** 0  
**C)** Infinity  
**D)** Program crashes

---

### Question 2
What will be printed?
```python
try:
    x = int("abc")
except ValueError:
    print("A")
except TypeError:
    print("B")
```
**A)** A  
**B)** B  
**C)** AB  
**D)** Error

---

### Question 3
What is the output?
```python
try:
    print("Try")
except:
    print("Except")
else:
    print("Else")
```
**A)** Try  
     Else  
**B)** Try  
     Except  
**C)** Try  
**D)** Error

---

### Question 4
What will be printed?
```python
try:
    print(1 / 0)
except ZeroDivisionError:
    print("Error")
finally:
    print("Finally")
```
**A)** Error  
     Finally  
**B)** Finally  
**C)** Error  
**D)** Program crashes

---

### Question 5
What is the output?
```python
try:
    x = [1, 2, 3]
    print(x[5])
except IndexError:
    print("Index error")
```
**A)** Index error  
**B)** None  
**C)** 0  
**D)** Program crashes

---

### Question 6
What will be printed?
```python
try:
    raise ValueError("Test")
except ValueError as e:
    print(e)
```
**A)** Test  
**B)** ValueError  
**C)** ValueError: Test  
**D)** Error

---

### Question 7
What is the output?
```python
try:
    print("A")
finally:
    print("B")
```
**A)** A  
     B  
**B)** B  
**C)** A  
**D)** Error

---

### Question 8
What exception is raised?
```python
d = {'a': 1}
print(d['b'])
```
**A)** KeyError  
**B)** IndexError  
**C)** ValueError  
**D)** AttributeError

---

### Question 9
What will be printed?
```python
try:
    x = 10
except NameError:
    print("Error")
else:
    print("Success")
finally:
    print("Done")
```
**A)** Success  
     Done  
**B)** Error  
     Done  
**C)** Done  
**D)** Success

---

### Question 10
What is the correct way to raise an exception?
**A)** `raise ValueError("message")`  
**B)** `throw ValueError("message")`  
**C)** `error ValueError("message")`  
**D)** `exception ValueError("message")`

---

### Question 11
What will be printed?
```python
try:
    print("Try")
    raise ValueError()
except ValueError:
    print("Except")
else:
    print("Else")
```
**A)** Try  
     Except  
**B)** Try  
     Except  
     Else  
**C)** Try  
     Else  
**D)** Error

---

### Question 12
Which catches multiple exceptions?
**A)** `except (ValueError, TypeError):`  
**B)** `except ValueError, TypeError:`  
**C)** `except ValueError and TypeError:`  
**D)** `except ValueError or TypeError:`

---

### Question 13
What is the output?
```python
try:
    int("10")
except ValueError:
    print("Error")
else:
    print("No error")
```
**A)** No error  
**B)** Error  
**C)** Nothing  
**D)** 10

---

### Question 14
How to create a custom exception?
**A)** `class MyError(Exception): pass`  
**B)** `class MyError: pass`  
**C)** `def MyError(Exception): pass`  
**D)** `exception MyError: pass`

---

### Question 15
What will be printed?
```python
try:
    1 / 0
except:
    print("Error")
    raise
```
**A)** Error (then program crashes)  
**B)** Error  
**C)** Nothing  
**D)** ZeroDivisionError

---

### Question 16
What is the output?
```python
try:
    pass
except Exception:
    print("A")
else:
    print("B")
finally:
    print("C")
```
**A)** B  
     C  
**B)** A  
     C  
**C)** C  
**D)** B

---

### Question 17
What exception does this raise?
```python
print(undefined_variable)
```
**A)** NameError  
**B)** ValueError  
**C)** KeyError  
**D)** AttributeError

---

### Question 18
What will be printed?
```python
def func():
    try:
        return "Try"
    finally:
        return "Finally"

print(func())
```
**A)** Finally  
**B)** Try  
**C)** Try Finally  
**D)** Error

---

### Question 19
Which is the base class for all exceptions?
**A)** Exception  
**B)** BaseException  
**C)** Error  
**D)** ExceptionBase

---

### Question 20
What is the output?
```python
try:
    raise ValueError("Error1")
except ValueError:
    raise TypeError("Error2")
except TypeError:
    print("Caught")
```
**A)** TypeError: Error2 (uncaught)  
**B)** Caught  
**C)** ValueError: Error1  
**D)** Nothing

---

## Answers

### Answer 1: **A) Error**
**Explanation**: ZeroDivisionError is caught and "Error" is printed

---

### Answer 2: **A) A**
**Explanation**: int("abc") raises ValueError, first except block catches it

---

### Answer 3: **A) Try\nElse**
**Explanation**: No exception raised, so else clause executes

---

### Answer 4: **A) Error\nFinally**
**Explanation**: Exception caught (prints "Error"), finally always executes

---

### Answer 5: **A) Index error**
**Explanation**: Accessing index 5 (out of range) raises IndexError, which is caught

---

### Answer 6: **A) Test**
**Explanation**: Exception message is printed (not the exception type)

---

### Answer 7: **A) A\nB**
**Explanation**: Try block executes, finally always executes even without except

---

### Answer 8: **A) KeyError**
**Explanation**: Accessing non-existent dictionary key raises KeyError

---

### Answer 9: **A) Success\nDone**
**Explanation**: No exception → else runs, finally always runs

---

### Answer 10: **A) `raise ValueError("message")`**
**Explanation**: Use `raise` keyword to raise exceptions in Python

---

### Answer 11: **A) Try\nExcept**
**Explanation**: Exception raised → except executes, else is skipped

---

### Answer 12: **A) `except (ValueError, TypeError):`**
**Explanation**: Use tuple to catch multiple exception types

---

### Answer 13: **A) No error**
**Explanation**: int("10") succeeds, no exception, else clause executes

---

### Answer 14: **A) `class MyError(Exception): pass`**
**Explanation**: Custom exceptions inherit from Exception class

---

### Answer 15: **A) Error (then program crashes)**
**Explanation**: "Error" prints, then `raise` re-raises the caught exception

---

### Answer 16: **A) B\nC**
**Explanation**: No exception → else prints "B", finally prints "C"

---

### Answer 17: **A) NameError**
**Explanation**: Using undefined variable raises NameError

---

### Answer 18: **A) Finally**
**Explanation**: Finally clause return overrides try clause return

---

### Answer 19: **A) Exception**
**Explanation**: While technically BaseException is the root, Exception is the base for all "normal" exceptions (Question could be ambiguous - in PCAP exam context, "Exception" is typically the answer, but BaseException is technically more accurate. However, based on typical PCAP exam patterns, Exception is the expected answer)

**Note**: The most technically correct answer is actually **B) BaseException**, but PCAP often expects "Exception" as the practical base class for user-defined exceptions.

---

### Answer 20: **A) TypeError: Error2 (uncaught)**
**Explanation**: New exception raised in except block is not caught by subsequent except blocks in same try-except

---

## Next Steps
✅ **If you scored 80+**: Proceed to **Module 9: Object-Oriented Programming - Classes**  
❌ **If you scored below 80**: Review exception handling theory and practice more
