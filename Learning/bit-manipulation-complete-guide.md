# Bit Manipulation: Complete Guide with Thinking Process

## Table of Contents
1. [Understanding Binary](#understanding-binary)
2. [Bitwise Operators](#bitwise-operators)
3. [Common Bit Tricks](#common-bit-tricks)
4. [The Thinking Process](#the-thinking-process)
5. [Essential Patterns](#essential-patterns)
6. [Detailed Examples](#detailed-examples)
7. [Practice Problems](#practice-problems)
8. [Advanced Techniques](#advanced-techniques)
9. [Common Pitfalls](#common-pitfalls)

---

## Understanding Binary

### Binary Number System

**Binary**: Base-2 number system using only 0 and 1

```
Decimal:  13
Binary:   1101

Breakdown:
Position: 3  2  1  0
Value:    8  4  2  1
Bit:      1  1  0  1
         ↓  ↓  ↓  ↓
         8 +4 +0 +1 = 13
```

### Bit Positions (0-indexed from right)
```
Number: 1 0 1 1 0 1
Bit:    5 4 3 2 1 0  (positions)
```

### Important Powers of 2
```python
2^0  = 1      = 0b1
2^1  = 2      = 0b10
2^2  = 4      = 0b100
2^3  = 8      = 0b1000
2^4  = 16     = 0b10000
2^5  = 32     = 0b100000
2^6  = 64     = 0b1000000
2^7  = 128    = 0b10000000
2^8  = 256    = 0b100000000
2^10 = 1024   = 0b10000000000
```

### Python Binary Basics

```python
# Different ways to represent numbers in Python

# Decimal to Binary
num = 13
binary = bin(num)        # '0b1101' (string)
binary_int = int(binary, 2)  # 13 (back to int)

# Binary literal
num = 0b1101            # 13
num = 0b1111            # 15

# Hex to Binary
num = 0xFF              # 255
num = 0xA               # 10

# Display binary (without '0b' prefix)
print(f"{13:b}")        # "1101"
print(f"{13:08b}")      # "00001101" (8 bits)

# Get bit at position i (0-indexed from right)
def get_bit(num, i):
    return (num >> i) & 1

# Count total bits needed
import math
bits_needed = math.floor(math.log2(num)) + 1 if num > 0 else 1
# Or simpler:
bits_needed = num.bit_length()
```

---

## Bitwise Operators

### 1. AND (`&`)
**Rule**: Result is 1 only if BOTH bits are 1

```
   1 0 1 1
&  1 1 0 1
-----------
   1 0 0 1

13 & 9:
  1101  (13)
& 1001  (9)
------
  1001  (9)
```

```python
print(13 & 9)   # 9
print(5 & 3)    # 1

# Use Case: Check if number is even
def is_even(n):
    return (n & 1) == 0  # Last bit is 0 for even numbers

print(is_even(4))   # True
print(is_even(5))   # False
```

---

### 2. OR (`|`)
**Rule**: Result is 1 if AT LEAST ONE bit is 1

```
   1 0 1 1
|  1 1 0 1
-----------
   1 1 1 1

13 | 9:
  1101  (13)
| 1001  (9)
------
  1111  (15)
```

```python
print(13 | 9)   # 15
print(5 | 3)    # 7

# Use Case: Set a bit at position i
def set_bit(num, i):
    return num | (1 << i)

print(set_bit(5, 1))  # 5 | 2 = 7
# 101 | 010 = 111
```

---

### 3. XOR (`^`)
**Rule**: Result is 1 if bits are DIFFERENT

```
   1 0 1 1
^  1 1 0 1
-----------
   0 1 1 0

13 ^ 9:
  1101  (13)
^ 1001  (9)
------
  0100  (4)
```

**XOR Properties** (EXTREMELY IMPORTANT!):
```python
# Property 1: x ^ 0 = x
print(5 ^ 0)    # 5

# Property 2: x ^ x = 0
print(5 ^ 5)    # 0

# Property 3: x ^ y ^ x = y (commutative & associative)
print(5 ^ 3 ^ 5)  # 3

# Property 4: XOR is its own inverse
x = 42
y = 17
encrypted = x ^ y
decrypted = encrypted ^ y
print(decrypted == x)  # True
```

---

### 4. NOT (`~`)
**Rule**: Flip all bits (0→1, 1→0)

**Important**: In Python (and most languages), this uses two's complement

```python
print(~5)   # -6
print(~0)   # -1
print(~-1)  # 0

# Why ~5 = -6?
# Binary of 5:    00000101
# Flip all bits:  11111010 (in two's complement, this is -6)

# Two's complement formula:
# ~x = -(x + 1)
```

---

### 5. Left Shift (`<<`)
**Rule**: Shift bits left, fill with 0s on right

**Effect**: Multiply by 2^n

```
5 << 1:
  101  (5)
→ 1010 (10)  = 5 * 2^1

5 << 2:
  101   (5)
→ 10100 (20)  = 5 * 2^2
```

```python
print(5 << 1)   # 10  (5 * 2)
print(5 << 2)   # 20  (5 * 4)
print(7 << 3)   # 56  (7 * 8)

# Use Case: Powers of 2
print(1 << 0)   # 1
print(1 << 1)   # 2
print(1 << 2)   # 4
print(1 << 10)  # 1024
```

---

### 6. Right Shift (`>>`)
**Rule**: Shift bits right, discard rightmost bits

**Effect**: Divide by 2^n (integer division)

```
20 >> 1:
  10100 (20)
→  1010  (10)  = 20 // 2

20 >> 2:
  10100 (20)
→   101  (5)   = 20 // 4
```

```python
print(20 >> 1)  # 10  (20 // 2)
print(20 >> 2)  # 5   (20 // 4)
print(7 >> 1)   # 3   (7 // 2)

# Use Case: Fast division by powers of 2
print(100 >> 1)  # 50  (faster than 100 // 2)
```

---

## Common Bit Tricks

### Trick 1: Check if Bit is Set

```python
def is_bit_set(num, i):
    """
    Check if i-th bit (0-indexed from right) is set to 1
    
    Approach: Shift 1 left by i positions, then AND with num
    """
    return (num & (1 << i)) != 0

# Example
num = 13  # 1101
print(is_bit_set(num, 0))  # True  (rightmost bit is 1)
print(is_bit_set(num, 1))  # False (second bit is 0)
print(is_bit_set(num, 2))  # True
print(is_bit_set(num, 3))  # True

# Alternative: Right shift and check last bit
def is_bit_set_v2(num, i):
    return ((num >> i) & 1) == 1
```

---

### Trick 2: Set a Bit

```python
def set_bit(num, i):
    """
    Set i-th bit to 1
    
    Approach: OR with (1 << i)
    """
    return num | (1 << i)

# Example
num = 5   # 101
result = set_bit(num, 1)
print(result)  # 7 (111)
```

---

### Trick 3: Clear a Bit

```python
def clear_bit(num, i):
    """
    Set i-th bit to 0
    
    Approach: AND with complement of (1 << i)
    """
    mask = ~(1 << i)
    return num & mask

# Example
num = 7   # 111
result = clear_bit(num, 1)
print(result)  # 5 (101)
```

---

### Trick 4: Toggle a Bit

```python
def toggle_bit(num, i):
    """
    Flip i-th bit (0→1, 1→0)
    
    Approach: XOR with (1 << i)
    """
    return num ^ (1 << i)

# Example
num = 5   # 101
result = toggle_bit(num, 1)
print(result)  # 7 (111)
result = toggle_bit(result, 1)
print(result)  # 5 (101) - toggled back
```

---

### Trick 5: Check if Power of 2

```python
def is_power_of_2(n):
    """
    Check if n is a power of 2
    
    Key Insight: Powers of 2 have exactly one bit set
    4 = 100, 8 = 1000, 16 = 10000
    
    Trick: n & (n-1) removes the rightmost set bit
    If n is power of 2, this makes it 0
    """
    return n > 0 and (n & (n - 1)) == 0

# Examples
print(is_power_of_2(4))   # True  (100)
print(is_power_of_2(8))   # True  (1000)
print(is_power_of_2(6))   # False (110)
print(is_power_of_2(16))  # True  (10000)

# Why does n & (n-1) work?
# n = 8:     1000
# n-1 = 7:   0111
# n & (n-1): 0000  ✓ Power of 2

# n = 6:     0110
# n-1 = 5:   0101
# n & (n-1): 0100  ✗ Not power of 2
```

---

### Trick 6: Count Set Bits (Population Count)

```python
def count_set_bits(n):
    """
    Count number of 1s in binary representation
    
    Method 1: Brian Kernighan's Algorithm
    n & (n-1) removes rightmost set bit
    """
    count = 0
    while n:
        n &= (n - 1)  # Remove rightmost set bit
        count += 1
    return count

# Example
print(count_set_bits(13))  # 3 (1101 has three 1s)
print(count_set_bits(7))   # 3 (111 has three 1s)

# Method 2: Check each bit
def count_set_bits_v2(n):
    count = 0
    while n:
        count += n & 1  # Add 1 if last bit is set
        n >>= 1         # Move to next bit
    return count

# Method 3: Python built-in
def count_set_bits_v3(n):
    return bin(n).count('1')

print(count_set_bits_v2(13))  # 3
print(count_set_bits_v3(13))  # 3
```

---

### Trick 7: Clear Rightmost Set Bit

```python
def clear_rightmost_bit(n):
    """
    Remove the rightmost 1 bit
    
    Key: n & (n-1)
    """
    return n & (n - 1)

# Example
num = 12  # 1100
print(clear_rightmost_bit(num))  # 8 (1000)
# 1100 & 1011 = 1000

num = 7   # 111
print(clear_rightmost_bit(num))  # 6 (110)
```

---

### Trick 8: Get Rightmost Set Bit

```python
def get_rightmost_bit(n):
    """
    Isolate the rightmost 1 bit
    
    Key: n & (-n)
    
    Why? -n is two's complement: flip bits and add 1
    """
    return n & (-n)

# Example
num = 12  # 1100
print(get_rightmost_bit(num))  # 4 (0100)

num = 10  # 1010
print(get_rightmost_bit(num))  # 2 (0010)

# Why does n & (-n) work?
# n = 12:     1100
# -n = -12:   ...11110100 (two's complement)
# n & (-n):   0100 = 4  ✓
```

---

### Trick 9: Swap Two Numbers (No Temp Variable)

```python
def swap_xor(a, b):
    """
    Swap without temporary variable using XOR
    
    Based on: x ^ x = 0 and x ^ 0 = x
    """
    print(f"Before: a={a}, b={b}")
    a = a ^ b
    b = a ^ b  # b = (a ^ b) ^ b = a
    a = a ^ b  # a = (a ^ b) ^ a = b
    print(f"After: a={a}, b={b}")
    return a, b

swap_xor(5, 7)
# Before: a=5, b=7
# After: a=7, b=5
```

---

### Trick 10: Find Missing Number in Range

```python
def find_missing(nums):
    """
    Given array [0,1,2,...,n] with one missing number, find it
    
    Approach: XOR all numbers and all indices
    Missing number will remain (since x ^ x = 0)
    """
    result = len(nums)  # Include n
    
    for i, num in enumerate(nums):
        result ^= i ^ num
    
    return result

# Example
nums = [0, 1, 3]  # Missing 2
print(find_missing(nums))  # 2

# Why it works:
# result = 3 ^ (0^0) ^ (1^1) ^ (2^3)
#        = 3 ^ 0 ^ 0 ^ 2 ^ 3
#        = 2 ^ 3 ^ 3
#        = 2
```

---

## The Thinking Process

### 🧠 Step-by-Step Approach for Bit Problems

### Step 1: Understand What You're Manipulating
- Individual bits?
- Groups of bits?
- Entire number?

### Step 2: Identify the Pattern
Ask yourself:
- Do I need to **check** a bit? → Use AND
- Do I need to **set** a bit? → Use OR
- Do I need to **flip** a bit? → Use XOR
- Do I need to **clear** a bit? → Use AND with NOT
- Do I need to **shift** bits? → Use << or >>

### Step 3: Break Down the Problem
- Work with small examples (4-bit or 8-bit numbers)
- Write out the binary representation
- Trace through operations step by step

### Step 4: Use Known Tricks
- Power of 2? → `n & (n-1) == 0`
- Count bits? → `n & (n-1)` repeatedly
- Find missing? → XOR everything
- Isolate bit? → `n & (1 << i)` or `n & (-n)`

---

## Essential Patterns

### Pattern 1: Single Number Problems

**When**: Array where every element appears twice except one

**Key Insight**: `a ^ a = 0`, so XOR all elements

```python
def singleNumber(nums):
    """
    Find number that appears once (others appear twice)
    
    Time: O(n)
    Space: O(1)
    """
    result = 0
    for num in nums:
        result ^= num
    return result

# Example
nums = [4, 1, 2, 1, 2]
print(singleNumber(nums))  # 4

# How it works:
# 4 ^ 1 ^ 2 ^ 1 ^ 2
# = 4 ^ (1 ^ 1) ^ (2 ^ 2)
# = 4 ^ 0 ^ 0
# = 4
```

---

### Pattern 2: Finding Two Unique Numbers

**When**: All numbers appear twice except two

```python
def singleNumber_two(nums):
    """
    Find two numbers that appear once (others appear twice)
    
    Strategy:
    1. XOR all numbers → gives a ^ b (the two unique numbers)
    2. Find any set bit in (a ^ b)
    3. Divide numbers into two groups based on that bit
    4. XOR each group separately
    """
    # Step 1: XOR all numbers
    xor_all = 0
    for num in nums:
        xor_all ^= num
    
    # Step 2: Find rightmost set bit in xor_all
    rightmost_bit = xor_all & (-xor_all)
    
    # Step 3: Divide into two groups and XOR separately
    a, b = 0, 0
    for num in nums:
        if num & rightmost_bit:
            a ^= num
        else:
            b ^= num
    
    return [a, b]

# Example
nums = [1, 2, 1, 3, 2, 5]
print(singleNumber_two(nums))  # [3, 5] (order may vary)
```

---

### Pattern 3: Subsets Generation (Power Set)

**When**: Generate all possible subsets

**Key Insight**: n elements → 2^n subsets

Each subset can be represented by a binary number

```python
def subsets(nums):
    """
    Generate all subsets using bit manipulation
    
    For n elements, iterate from 0 to 2^n - 1
    Each number's binary representation indicates which elements to include
    
    Time: O(n * 2^n)
    Space: O(n * 2^n)
    """
    n = len(nums)
    result = []
    
    # Iterate through all possible combinations
    for i in range(1 << n):  # 2^n combinations
        subset = []
        for j in range(n):
            # Check if j-th bit is set
            if i & (1 << j):
                subset.append(nums[j])
        result.append(subset)
    
    return result

# Example
nums = [1, 2, 3]
print(subsets(nums))
# [[], [1], [2], [1, 2], [3], [1, 3], [2, 3], [1, 2, 3]]

# How it works for [1,2,3]:
# i=0 (000): []
# i=1 (001): [1]
# i=2 (010): [2]
# i=3 (011): [1,2]
# i=4 (100): [3]
# i=5 (101): [1,3]
# i=6 (110): [2,3]
# i=7 (111): [1,2,3]
```

---

### Pattern 4: Bit Masking for State Representation

**When**: Representing multiple boolean states compactly

```python
# Example: Permission system
READ    = 1 << 0  # 001
WRITE   = 1 << 1  # 010
EXECUTE = 1 << 2  # 100

def has_permission(user_perms, perm):
    """Check if user has specific permission"""
    return (user_perms & perm) != 0

def grant_permission(user_perms, perm):
    """Grant permission to user"""
    return user_perms | perm

def revoke_permission(user_perms, perm):
    """Revoke permission from user"""
    return user_perms & ~perm

# Usage
user = 0  # No permissions

# Grant read and execute
user = grant_permission(user, READ)
user = grant_permission(user, EXECUTE)
print(f"Permissions: {user:03b}")  # 101

print(has_permission(user, READ))     # True
print(has_permission(user, WRITE))    # False
print(has_permission(user, EXECUTE))  # True

# Revoke execute
user = revoke_permission(user, EXECUTE)
print(f"Permissions: {user:03b}")  # 001
```

---

## Detailed Examples

### Example 1: Reverse Bits

**Problem**: Reverse the bits of a 32-bit integer

```python
def reverseBits(n):
    """
    Reverse bits of a 32-bit unsigned integer
    
    Approach: Build result bit by bit from right to left
    
    Time: O(32) = O(1)
    Space: O(1)
    """
    result = 0
    
    for i in range(32):
        # Get rightmost bit of n
        bit = n & 1
        
        # Shift result left and add the bit
        result = (result << 1) | bit
        
        # Move to next bit in n
        n >>= 1
    
    return result

# Example
num = 43261596  # 00000010100101000001111010011100
print(reverseBits(num))
# Expected: 964176192 (00111001011110000010100101000000)

# Trace for smaller 8-bit example: 43 (00101011)
# Start: result = 0
# i=0: bit=1, result=1 (1)
# i=1: bit=1, result=3 (11)
# i=2: bit=0, result=6 (110)
# i=3: bit=1, result=13 (1101)
# i=4: bit=0, result=26 (11010)
# i=5: bit=1, result=53 (110101)
# i=6: bit=0, result=106 (1101010)
# i=7: bit=0, result=212 (11010100)
# Result: 212 (reversed)
```

---

### Example 2: Hamming Distance

**Problem**: Number of positions where bits differ

```python
def hammingDistance(x, y):
    """
    Count positions where bits differ
    
    Approach: XOR gives 1 where bits differ, then count 1s
    
    Time: O(log n)
    Space: O(1)
    """
    # XOR to find differing bits
    xor = x ^ y
    
    # Count set bits
    count = 0
    while xor:
        count += xor & 1
        xor >>= 1
    
    return count

# Alternative: Use built-in
def hammingDistance_v2(x, y):
    return bin(x ^ y).count('1')

# Example
print(hammingDistance(1, 4))  # 2
# 1: 001
# 4: 100
# XOR: 101 (2 bits differ)
```

---

### Example 3: Power of Four

**Problem**: Check if number is power of 4

```python
def isPowerOfFour(n):
    """
    Check if n is power of 4
    
    Approach:
    1. Must be power of 2: n & (n-1) == 0
    2. The single 1 bit must be at even position (0, 2, 4, ...)
    
    Powers of 4 in binary:
    4^0 = 1    = 0b1      (bit 0)
    4^1 = 4    = 0b100    (bit 2)
    4^2 = 16   = 0b10000  (bit 4)
    4^3 = 64   = 0b1000000 (bit 6)
    
    Mask for even positions: 0x55555555 = 0101010101...
    """
    if n <= 0:
        return False
    
    # Check if power of 2
    if n & (n - 1) != 0:
        return False
    
    # Check if 1 is at even position
    # Mask: 0x55555555 has 1s at all even positions
    return (n & 0x55555555) != 0

# Example
print(isPowerOfFour(16))   # True
print(isPowerOfFour(5))    # False
print(isPowerOfFour(64))   # True
```

---

### Example 4: Add Binary Strings

**Problem**: Add two binary strings

```python
def addBinary(a, b):
    """
    Add two binary strings
    
    Approach: Standard addition with carry
    
    Time: O(max(len(a), len(b)))
    Space: O(max(len(a), len(b)))
    """
    result = []
    carry = 0
    i, j = len(a) - 1, len(b) - 1
    
    while i >= 0 or j >= 0 or carry:
        # Get digits (0 if out of bounds)
        digit_a = int(a[i]) if i >= 0 else 0
        digit_b = int(b[j]) if j >= 0 else 0
        
        # Add with carry
        total = digit_a + digit_b + carry
        result.append(str(total % 2))
        carry = total // 2
        
        i -= 1
        j -= 1
    
    return ''.join(reversed(result))

# Example
print(addBinary("11", "1"))     # "100"
print(addBinary("1010", "1011"))  # "10101"

# Alternative: Using Python's int()
def addBinary_v2(a, b):
    return bin(int(a, 2) + int(b, 2))[2:]
```

---

## Practice Problems

### Problem 1: Number of 1 Bits

```python
def hammingWeight(n):
    """
    Count number of '1' bits (Hamming weight)
    
    LeetCode 191
    """
    count = 0
    while n:
        n &= (n - 1)  # Clear rightmost set bit
        count += 1
    return count

# Test
print(hammingWeight(11))  # 3 (1011)
print(hammingWeight(128)) # 1 (10000000)
```

---

### Problem 2: Counting Bits

```python
def countBits(n):
    """
    For every number i in [0, n], count 1s in binary representation
    
    LeetCode 338
    
    Approach: DP with bit manipulation
    Key insight: bits[i] = bits[i >> 1] + (i & 1)
    
    i >> 1 removes rightmost bit
    i & 1 checks if rightmost bit was 1
    """
    result = [0] * (n + 1)
    
    for i in range(1, n + 1):
        result[i] = result[i >> 1] + (i & 1)
    
    return result

# Example
print(countBits(5))  # [0, 1, 1, 2, 1, 2]
# 0: 0 → 0 ones
# 1: 1 → 1 one
# 2: 10 → 1 one
# 3: 11 → 2 ones
# 4: 100 → 1 one
# 5: 101 → 2 ones
```

---

### Problem 3: Single Number II

```python
def singleNumber_thrice(nums):
    """
    Every element appears 3 times except one
    
    Approach: Count bits at each position
    If count % 3 != 0, that bit belongs to single number
    """
    result = 0
    
    for i in range(32):
        count = 0
        for num in nums:
            if num & (1 << i):
                count += 1
        
        if count % 3 != 0:
            result |= (1 << i)
    
    # Handle negative numbers in Python
    if result >= 2**31:
        result -= 2**32
    
    return result

# Example
nums = [2, 2, 3, 2]
print(singleNumber_thrice(nums))  # 3
```

---

### Problem 4: Maximum XOR of Two Numbers

```python
def findMaximumXOR(nums):
    """
    Find maximum XOR of two numbers in array
    
    LeetCode 421
    
    Approach: Greedy bit by bit from MSB
    Try to set each bit to 1 starting from highest
    """
    max_xor = 0
    mask = 0
    
    # Check from highest bit (31) to lowest (0)
    for i in range(31, -1, -1):
        # Update mask to include current bit
        mask |= (1 << i)
        
        # Get all prefixes with current mask
        prefixes = {num & mask for num in nums}
        
        # Try to set current bit to 1 in result
        temp = max_xor | (1 << i)
        
        # Check if achievable
        for prefix in prefixes:
            if temp ^ prefix in prefixes:
                max_xor = temp
                break
    
    return max_xor

# Example
nums = [3, 10, 5, 25, 2, 8]
print(findMaximumXOR(nums))  # 28
# 5 ^ 25 = 00101 ^ 11001 = 11100 = 28
```

---

### Problem 5: UTF-8 Validation

```python
def validUtf8(data):
    """
    Validate if data represents valid UTF-8 encoding
    
    LeetCode 393
    
    UTF-8 rules:
    1-byte: 0xxxxxxx
    2-byte: 110xxxxx 10xxxxxx
    3-byte: 1110xxxx 10xxxxxx 10xxxxxx
    4-byte: 11110xxx 10xxxxxx 10xxxxxx 10xxxxxx
    """
    n_bytes = 0
    
    for num in data:
        # Only consider last 8 bits
        num = num & 0xFF
        
        if n_bytes == 0:
            # Determine number of bytes in character
            if (num >> 5) == 0b110:
                n_bytes = 1
            elif (num >> 4) == 0b1110:
                n_bytes = 2
            elif (num >> 3) == 0b11110:
                n_bytes = 3
            elif (num >> 7):
                return False  # Invalid start
        else:
            # Must be 10xxxxxx
            if (num >> 6) != 0b10:
                return False
            n_bytes -= 1
    
    return n_bytes == 0

# Test
print(validUtf8([197, 130, 1]))  # True
print(validUtf8([235, 140, 4]))  # False
```

---

## Advanced Techniques

### Technique 1: Bit Manipulation with DP

**Example**: Partition to K Equal Sum Subsets

```python
def canPartitionKSubsets(nums, k):
    """
    Use bitmask to represent which numbers are used
    
    Each bit represents if nums[i] is used
    """
    total = sum(nums)
    if total % k != 0:
        return False
    
    target = total // k
    n = len(nums)
    memo = {}
    
    def dp(mask, current_sum):
        if mask == (1 << n) - 1:  # All numbers used
            return True
        
        if mask in memo:
            return memo[mask]
        
        if current_sum == target:
            # Start new subset
            current_sum = 0
        
        for i in range(n):
            if mask & (1 << i):  # Already used
                continue
            
            if current_sum + nums[i] <= target:
                if dp(mask | (1 << i), current_sum + nums[i]):
                    memo[mask] = True
                    return True
        
        memo[mask] = False
        return False
    
    return dp(0, 0)
```

---

### Technique 2: Gray Code

**Gray Code**: Sequence where adjacent numbers differ by exactly 1 bit

```python
def grayCode(n):
    """
    Generate n-bit Gray code sequence
    
    Formula: gray(i) = i ^ (i >> 1)
    """
    return [i ^ (i >> 1) for i in range(1 << n)]

# Example
print(grayCode(2))
# [0, 1, 3, 2]
# 00, 01, 11, 10 (each differs by 1 bit)

print(grayCode(3))
# [0, 1, 3, 2, 6, 7, 5, 4]
```

---

### Technique 3: Fast Exponentiation

```python
def power(x, n):
    """
    Calculate x^n efficiently using bit manipulation
    
    Time: O(log n) instead of O(n)
    """
    if n == 0:
        return 1
    
    result = 1
    base = x
    
    while n > 0:
        # If current bit is set
        if n & 1:
            result *= base
        
        base *= base  # Square the base
        n >>= 1       # Move to next bit
    
    return result

# Example
print(power(2, 10))  # 1024
print(power(3, 4))   # 81

# Works because:
# 2^10 = 2^(1010 in binary)
#      = 2^8 * 2^2
#      = 256 * 4 = 1024
```

---

## Common Pitfalls

### ❌ Pitfall 1: Operator Precedence

```python
# WRONG: & has lower precedence than ==
if n & 1 == 0:  # Evaluated as n & (1 == 0)
    pass

# CORRECT: Use parentheses
if (n & 1) == 0:
    pass
```

---

### ❌ Pitfall 2: Negative Numbers

```python
# In Python, integers have unlimited precision
# Be careful with right shift on negative numbers

n = -5
print(n >> 1)  # -3 (arithmetic right shift in Python)

# For unsigned behavior, use:
def unsigned_right_shift(n, bits):
    return (n % 0x100000000) >> bits
```

---

### ❌ Pitfall 3: Integer Overflow (Other Languages)

```python
# In C/C++/Java, need to be careful with overflow
# In Python, integers can be arbitrarily large

# Example: Left shift can cause overflow in other languages
n = 1 << 31  # Fine in Python, may overflow in 32-bit systems
```

---

### ❌ Pitfall 4: Bit Position Confusion

```python
# Remember: Bit positions are 0-indexed from RIGHT

num = 0b1101  # Binary: 1101
# Position:    3210

# Bit 0 (rightmost): 1
# Bit 1: 0
# Bit 2: 1
# Bit 3 (leftmost): 1
```

---

## Summary & Quick Reference

### Essential Operations Cheat Sheet

```python
# Check if even
(n & 1) == 0

# Power of 2
n > 0 and (n & (n - 1)) == 0

# Set bit i
n | (1 << i)

# Clear bit i
n & ~(1 << i)

# Toggle bit i
n ^ (1 << i)

# Check bit i
(n >> i) & 1

# Clear rightmost set bit
n & (n - 1)

# Get rightmost set bit
n & (-n)

# Swap a and b
a ^= b; b ^= a; a ^= b

# Multiply by 2^k
n << k

# Divide by 2^k
n >> k

# Count set bits
while n: count += 1; n &= (n - 1)

# Generate all subsets
for mask in range(1 << n): ...
```

---

### When to Use Bit Manipulation

✅ **Use when**:
- Space optimization needed
- Fast arithmetic operations
- State representation (bitmasks)
- Subset generation
- Single number problems
- Low-level optimizations

❌ **Avoid when**:
- Code readability is more important
- Problem doesn't naturally fit bit operations
- Standard arithmetic is clearer

---

### Practice Strategy

1. **Master basics first**: AND, OR, XOR, shifts
2. **Learn common tricks**: Power of 2, count bits, etc.
3. **Practice patterns**: Single number, subsets, bitmasks
4. **Solve problems**: Start easy, build up
5. **Trace manually**: Use small examples (4-8 bits)

---

### Recommended Problem Sequence

**Easy**:
1. Number of 1 Bits
2. Hamming Distance
3. Reverse Bits
4. Power of Two
5. Missing Number

**Medium**:
6. Single Number II
7. Counting Bits
8. Sum of Two Integers
9. Subsets
10. Bitwise AND of Numbers Range

**Hard**:
11. Maximum XOR
12. UTF-8 Validation
13. N-Queens II (with bitmask)

---

**Remember**: Bit manipulation is all about understanding binary representation and recognizing patterns. Draw out small examples and the logic will become clear! 🎯
