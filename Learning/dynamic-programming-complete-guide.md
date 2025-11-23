# Dynamic Programming: Complete Guide with Thinking Process

## Table of Contents
1. [What is Dynamic Programming?](#what-is-dynamic-programming)
2. [When to Use Dynamic Programming](#when-to-use-dynamic-programming)
3. [The Mental Framework](#the-mental-framework)
4. [Core Concepts](#core-concepts)
5. [The Step-by-Step Thinking Process](#the-step-by-step-thinking-process)
6. [Common DP Patterns](#common-dp-patterns)
7. [Detailed Examples](#detailed-examples)
8. [Practice Problems with Solutions](#practice-problems-with-solutions)
9. [Common Pitfalls and Tips](#common-pitfalls-and-tips)

---

## What is Dynamic Programming?

**Dynamic Programming (DP)** is an optimization technique that solves complex problems by:
1. Breaking them down into simpler **overlapping subproblems**
2. Storing the results of subproblems to avoid redundant calculations (**memoization**)
3. Building up solutions from smaller subproblems (**bottom-up approach**)

### The Key Insight
Instead of solving the same subproblem multiple times (like in naive recursion), we solve it **once** and **remember** the answer.

### Simple Analogy
Think of DP like taking notes in class:
- **Without DP (Naive Recursion)**: You forget everything and re-learn the same concept every time you need it
- **With DP**: You write it down once and refer to your notes whenever needed

---

## When to Use Dynamic Programming

### ✅ Use DP when you see these characteristics:

1. **Optimal Substructure**: The optimal solution can be constructed from optimal solutions of subproblems
2. **Overlapping Subproblems**: The same subproblems are solved multiple times
3. **Problem asks for**:
   - Maximum/Minimum value
   - Number of ways to do something
   - Is it possible to achieve something
   - Longest/Shortest subsequence/substring

### 🔴 Clues in Problem Statements:
- "Find the maximum/minimum..."
- "Count the number of ways..."
- "Is it possible to..."
- "Find the longest/shortest..."
- "Optimize..."

---

## The Mental Framework

### 🧠 Think of DP in Two Ways:

#### 1. **Top-Down (Memoization)**
- Start with the original problem
- Break it into subproblems recursively
- Store (memoize) results as you solve them
- Think: "To solve F(n), I need F(n-1) and F(n-2)"

#### 2. **Bottom-Up (Tabulation)**
- Start with the smallest subproblems
- Build up to the original problem iteratively
- Fill a table/array with solutions
- Think: "I know F(0) and F(1), so I can compute F(2), then F(3)..."

---

## Core Concepts

### 1. State
**Definition**: Variables that uniquely describe a subproblem

**Example**: In Fibonacci, the state is just the number `n`
- F(5) means "what is the 5th Fibonacci number?"

**Example**: In 0/1 Knapsack, the state is `(item_index, remaining_capacity)`
- dp[i][w] means "max value using first i items with capacity w"

### 2. Transition
**Definition**: How to compute the current state from previous states

**Example**: Fibonacci transition
```
F(n) = F(n-1) + F(n-2)
```

**Example**: Knapsack transition
```
dp[i][w] = max(
    dp[i-1][w],              # don't take item i
    dp[i-1][w-weight[i]] + value[i]  # take item i
)
```

### 3. Base Cases
**Definition**: The simplest subproblems that you can solve directly without recursion

**Example**: Fibonacci
```
F(0) = 0
F(1) = 1
```

### 4. Memoization Table / DP Array
**Definition**: Data structure to store computed results

- 1D array: `dp[i]`
- 2D array: `dp[i][j]`
- Dictionary: `memo = {}`

---

## The Step-by-Step Thinking Process

### 🎯 Follow these steps for ANY DP problem:

### Step 1: Identify if it's a DP problem
- Does it have optimal substructure?
- Are subproblems overlapping?
- Does it ask for optimization/counting/possibility?

### Step 2: Define the State
Ask yourself: **"What information do I need to track to solve a subproblem?"**

Examples:
- Fibonacci: "Which number am I computing?" → State: `n`
- Climbing Stairs: "Which step am I on?" → State: `step`
- Coin Change: "What amount do I need to make?" → State: `amount`
- 0/1 Knapsack: "Which items have I considered? What's my remaining capacity?" → State: `(index, capacity)`

### Step 3: Write the Recurrence Relation
Ask yourself: **"How can I solve this state using smaller states?"**

Think about what choices/decisions you can make at each step.

### Step 4: Identify Base Cases
Ask yourself: **"What are the simplest cases I know the answer to?"**

### Step 5: Decide on Implementation Approach
- **Memoization (Top-Down)**: More intuitive, easier to write initially
- **Tabulation (Bottom-Up)**: More efficient, better for interviews

### Step 6: Code It Up
Start with recursive solution → Add memoization → Convert to tabulation (optional)

### Step 7: Optimize
Can you reduce space complexity? (2D → 1D array)

---

## Common DP Patterns

### Pattern 1: Linear DP (1D)
**Characteristics**: Depends on previous states in a sequence

**Template**:
```python
dp = [0] * (n + 1)
dp[0] = base_case

for i in range(1, n + 1):
    dp[i] = function_of(dp[i-1], dp[i-2], ...)
```

**Example Problems**:
- Fibonacci Numbers
- Climbing Stairs
- House Robber
- Decode Ways

---

### Pattern 2: 2D DP (Grid/Matrix)
**Characteristics**: State depends on 2 variables

**Template**:
```python
dp = [[0] * (m + 1) for _ in range(n + 1)]
# Initialize base cases
dp[0][0] = base_case

for i in range(n + 1):
    for j in range(m + 1):
        dp[i][j] = function_of(dp[i-1][j], dp[i][j-1], dp[i-1][j-1], ...)
```

**Example Problems**:
- Longest Common Subsequence
- Edit Distance
- Unique Paths
- 0/1 Knapsack

---

### Pattern 3: Subsequence/Substring DP
**Characteristics**: Finding optimal subsequences or substrings

**Common States**:
- `dp[i]`: Best answer ending at index i
- `dp[i][j]`: Best answer for substring from i to j

**Example Problems**:
- Longest Increasing Subsequence
- Longest Common Subsequence
- Palindromic Substrings

---

### Pattern 4: Knapsack DP
**Characteristics**: Making optimal selections with constraints

**Template**:
```python
dp = [[0] * (capacity + 1) for _ in range(n + 1)]

for i in range(1, n + 1):
    for w in range(capacity + 1):
        # Choice: take item or not
        if weight[i-1] <= w:
            dp[i][w] = max(
                dp[i-1][w],  # don't take
                dp[i-1][w-weight[i-1]] + value[i-1]  # take
            )
        else:
            dp[i][w] = dp[i-1][w]
```

**Example Problems**:
- 0/1 Knapsack
- Subset Sum
- Partition Equal Subset Sum
- Target Sum

---

### Pattern 5: Decision Making DP
**Characteristics**: Making optimal decisions at each step

**Example Problems**:
- Buy and Sell Stock (with variations)
- House Robber
- Jump Game

---

## Detailed Examples

Let's work through problems with the complete thinking process.

---

## Example 1: Fibonacci Numbers (Foundation)

### Problem
Find the n-th Fibonacci number where F(0) = 0, F(1) = 1, and F(n) = F(n-1) + F(n-2).

### 🧠 Thinking Process

**Step 1**: Is this DP?
- Optimal substructure? ✅ F(n) depends on F(n-1) and F(n-2)
- Overlapping subproblems? ✅ F(5) → F(4) and F(3) → both need F(3), F(2)...

**Step 2**: Define State
- State: `n` (which Fibonacci number we want)

**Step 3**: Recurrence Relation
```
F(n) = F(n-1) + F(n-2)
```

**Step 4**: Base Cases
```
F(0) = 0
F(1) = 1
```

### Solution 1: Naive Recursion (Inefficient)

```python
def fib_naive(n):
    """
    Time: O(2^n) - exponential!
    Space: O(n) - recursion stack
    
    This recalculates the same values many times.
    Example: fib(5) calls fib(3) twice!
    """
    if n <= 1:
        return n
    return fib_naive(n - 1) + fib_naive(n - 2)

# Test
print(fib_naive(10))  # 55, but slow for large n
```

**Why is this slow?**
```
fib(5)
├── fib(4)
│   ├── fib(3)
│   │   ├── fib(2)
│   │   │   ├── fib(1) = 1
│   │   │   └── fib(0) = 0
│   │   └── fib(1) = 1
│   └── fib(2)  ← RECALCULATED!
│       ├── fib(1) = 1
│       └── fib(0) = 0
└── fib(3)  ← RECALCULATED AGAIN!
    ├── fib(2)
    │   ├── fib(1) = 1
    │   └── fib(0) = 0
    └── fib(1) = 1
```

### Solution 2: Top-Down with Memoization

```python
def fib_memo(n, memo=None):
    """
    Time: O(n) - each subproblem solved once
    Space: O(n) - memo dictionary + recursion stack
    
    Key insight: Store results to avoid recalculation
    """
    if memo is None:
        memo = {}
    
    # Base cases
    if n <= 1:
        return n
    
    # Check if already computed
    if n in memo:
        return memo[n]
    
    # Compute and store
    memo[n] = fib_memo(n - 1, memo) + fib_memo(n - 2, memo)
    return memo[n]

# Test
print(fib_memo(100))  # Fast even for large n!

# Alternative cleaner syntax with @lru_cache
from functools import lru_cache

@lru_cache(maxsize=None)
def fib_memo_clean(n):
    """Same as above but cleaner with decorator"""
    if n <= 1:
        return n
    return fib_memo_clean(n - 1) + fib_memo_clean(n - 2)

print(fib_memo_clean(100))
```

### Solution 3: Bottom-Up Tabulation

```python
def fib_tabulation(n):
    """
    Time: O(n)
    Space: O(n) - dp array
    
    Build from bottom up: start with known values, compute larger values
    """
    if n <= 1:
        return n
    
    # Create DP table
    dp = [0] * (n + 1)
    
    # Base cases
    dp[0] = 0
    dp[1] = 1
    
    # Fill table bottom-up
    for i in range(2, n + 1):
        dp[i] = dp[i - 1] + dp[i - 2]
    
    return dp[n]

print(fib_tabulation(100))
```

### Solution 4: Space Optimized

```python
def fib_optimized(n):
    """
    Time: O(n)
    Space: O(1) - only store last 2 values
    
    Observation: We only need the last 2 values, not the entire array!
    """
    if n <= 1:
        return n
    
    prev2 = 0  # F(0)
    prev1 = 1  # F(1)
    
    for i in range(2, n + 1):
        current = prev1 + prev2
        prev2 = prev1
        prev1 = current
    
    return prev1

print(fib_optimized(100))
```

---

## Example 2: Climbing Stairs (Classic Pattern)

### Problem
You're climbing stairs with `n` steps. You can climb 1 or 2 steps at a time. How many distinct ways can you climb to the top?

### 🧠 Thinking Process

**Step 1**: Is this DP?
- Asks for "number of ways" ✅
- Current step depends on previous steps ✅

**Step 2**: Define State
- State: `i` (current step number)
- `dp[i]` = number of ways to reach step i

**Step 3**: Recurrence Relation

Think: "How can I reach step i?"
- From step i-1 (take 1 step)
- From step i-2 (take 2 steps)

```
dp[i] = dp[i-1] + dp[i-2]
```

**Step 4**: Base Cases
```
dp[0] = 1  # One way to stay at ground (do nothing)
dp[1] = 1  # One way to reach step 1 (one 1-step)
```

### Solution: Bottom-Up

```python
def climbStairs(n):
    """
    Time: O(n)
    Space: O(n)
    
    It's Fibonacci in disguise!
    """
    if n <= 1:
        return 1
    
    dp = [0] * (n + 1)
    dp[0] = 1
    dp[1] = 1
    
    for i in range(2, n + 1):
        dp[i] = dp[i - 1] + dp[i - 2]
    
    return dp[n]

# Test
print(climbStairs(5))  # 8 ways

# Space Optimized O(1)
def climbStairs_optimized(n):
    if n <= 1:
        return 1
    
    prev2, prev1 = 1, 1
    
    for i in range(2, n + 1):
        current = prev1 + prev2
        prev2 = prev1
        prev1 = current
    
    return prev1

print(climbStairs_optimized(5))  # 8
```

### Visual Example
```
n = 5
Step 0: 1 way  (stay at ground)
Step 1: 1 way  (1)
Step 2: 2 ways (1+1, 2)
Step 3: 3 ways (1+1+1, 1+2, 2+1)
Step 4: 5 ways (previous 3 ways + step, previous 2 ways + 2 steps)
Step 5: 8 ways
```

---

## Example 3: Coin Change (Unbounded Knapsack)

### Problem
Given coins of different denominations and a total amount, find the minimum number of coins needed to make that amount. Return -1 if impossible.

Example: coins = [1, 2, 5], amount = 11 → Output: 3 (5 + 5 + 1)

### 🧠 Thinking Process

**Step 1**: Is this DP?
- Asks for minimum ✅
- Subproblems overlap (amount 11 can be broken into smaller amounts) ✅

**Step 2**: Define State
- State: `amount` (remaining amount to make)
- `dp[amount]` = minimum coins needed to make this amount

**Step 3**: Recurrence Relation

Think: "For each coin, I can either use it or not"

For amount `i`, try each coin:
```
dp[i] = min(dp[i - coin] + 1) for each coin where coin <= i
```

**Step 4**: Base Cases
```
dp[0] = 0  # Zero coins needed to make amount 0
```

### Solution: Bottom-Up

```python
def coinChange(coins, amount):
    """
    Time: O(amount * len(coins))
    Space: O(amount)
    
    Build up from amount 0 to target amount
    """
    # Initialize with impossible value
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0  # Base case
    
    # For each amount from 1 to target
    for i in range(1, amount + 1):
        # Try each coin
        for coin in coins:
            if coin <= i:
                # Take minimum of current and using this coin
                dp[i] = min(dp[i], dp[i - coin] + 1)
    
    # If still infinity, impossible
    return dp[amount] if dp[amount] != float('inf') else -1

# Test
coins = [1, 2, 5]
amount = 11
print(coinChange(coins, amount))  # 3 (5+5+1)

coins = [2]
amount = 3
print(coinChange(coins, amount))  # -1 (impossible)
```

### Visual Trace
```
coins = [1, 2, 5], amount = 11

dp[0] = 0
dp[1] = 1  (use coin 1)
dp[2] = 1  (use coin 2)
dp[3] = 2  (1+2 or 1+1+1, min is 2)
dp[4] = 2  (2+2)
dp[5] = 1  (use coin 5)
dp[6] = 2  (5+1)
dp[7] = 2  (5+2)
...
dp[11] = 3 (5+5+1)
```

---

## Example 4: Longest Increasing Subsequence (LIS)

### Problem
Find the length of the longest increasing subsequence in an array.

Example: [10, 9, 2, 5, 3, 7, 101, 18] → Output: 4 ([2, 3, 7, 101] or [2, 5, 7, 101])

### 🧠 Thinking Process

**Step 1**: Is this DP?
- Asks for "longest" ✅
- Subsequence problems are classic DP ✅

**Step 2**: Define State
- State: `i` (index in array)
- `dp[i]` = length of longest increasing subsequence **ending at index i**

**Step 3**: Recurrence Relation

Think: "For position i, which previous elements can I extend from?"

```
dp[i] = max(dp[j] + 1) for all j < i where arr[j] < arr[i]
```

**Step 4**: Base Cases
```
dp[i] = 1  # Each element is a subsequence of length 1 by itself
```

### Solution

```python
def lengthOfLIS(nums):
    """
    Time: O(n^2)
    Space: O(n)
    
    For each position, check all previous positions
    """
    if not nums:
        return 0
    
    n = len(nums)
    # Each element is a LIS of length 1 by itself
    dp = [1] * n
    
    for i in range(1, n):
        # Check all previous elements
        for j in range(i):
            # If we can extend from j
            if nums[j] < nums[i]:
                dp[i] = max(dp[i], dp[j] + 1)
    
    # Return maximum LIS length found
    return max(dp)

# Test
nums = [10, 9, 2, 5, 3, 7, 101, 18]
print(lengthOfLIS(nums))  # 4

# Example with trace
nums = [3, 1, 4, 1, 5]
print(lengthOfLIS(nums))  # 3 ([1, 4, 5])
```

### Visual Trace
```
nums = [10, 9, 2, 5, 3, 7, 101, 18]
         0   1  2  3  4  5   6    7

dp[0] = 1  (just [10])
dp[1] = 1  (just [9], can't extend from 10)
dp[2] = 1  (just [2])
dp[3] = 2  ([2, 5])
dp[4] = 2  ([2, 3])
dp[5] = 3  ([2, 5, 7] or [2, 3, 7])
dp[6] = 4  ([2, 5, 7, 101])
dp[7] = 4  ([2, 5, 7, 18])

max(dp) = 4
```

---

## Example 5: 0/1 Knapsack (2D DP Classic)

### Problem
Given weights and values of n items, and a knapsack capacity, find the maximum value you can carry. Each item can be used at most once.

Example:
- weights = [1, 2, 3]
- values = [6, 10, 12]
- capacity = 5
- Output: 22 (items 2 and 3)

### 🧠 Thinking Process

**Step 1**: Is this DP?
- Asks for maximum ✅
- Overlapping subproblems (same capacity with same items checked multiple times) ✅

**Step 2**: Define State
- State: `(i, w)` where i = first i items considered, w = remaining capacity
- `dp[i][w]` = max value using first i items with capacity w

**Step 3**: Recurrence Relation

Think: "For item i, I have 2 choices:"
1. **Don't take it**: `dp[i-1][w]`
2. **Take it** (if it fits): `dp[i-1][w-weight[i]] + value[i]`

```
dp[i][w] = max(
    dp[i-1][w],                          # don't take item i
    dp[i-1][w-weight[i]] + value[i]      # take item i (if fits)
)
```

**Step 4**: Base Cases
```
dp[0][w] = 0  # No items, value is 0
dp[i][0] = 0  # No capacity, value is 0
```

### Solution: 2D DP

```python
def knapsack(weights, values, capacity):
    """
    Time: O(n * capacity)
    Space: O(n * capacity)
    
    Build a 2D table
    """
    n = len(weights)
    # dp[i][w] = max value with first i items and capacity w
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]
    
    # Fill the table
    for i in range(1, n + 1):
        for w in range(capacity + 1):
            # Don't take item i-1
            dp[i][w] = dp[i-1][w]
            
            # Take item i-1 if it fits
            if weights[i-1] <= w:
                dp[i][w] = max(
                    dp[i][w],
                    dp[i-1][w - weights[i-1]] + values[i-1]
                )
    
    return dp[n][capacity]

# Test
weights = [1, 2, 3]
values = [6, 10, 12]
capacity = 5
print(knapsack(weights, values, capacity))  # 22
```

### Solution: Space Optimized (1D DP)

```python
def knapsack_optimized(weights, values, capacity):
    """
    Time: O(n * capacity)
    Space: O(capacity)
    
    Observation: We only need the previous row, not all rows
    """
    n = len(weights)
    dp = [0] * (capacity + 1)
    
    for i in range(n):
        # Traverse backwards to avoid overwriting needed values
        for w in range(capacity, weights[i] - 1, -1):
            dp[w] = max(dp[w], dp[w - weights[i]] + values[i])
    
    return dp[capacity]

print(knapsack_optimized(weights, values, capacity))  # 22
```

### Visual Trace (2D)
```
weights = [1, 2, 3]
values  = [6, 10, 12]
capacity = 5

     w=0  w=1  w=2  w=3  w=4  w=5
i=0    0    0    0    0    0    0
i=1    0    6    6    6    6    6  (item 0: w=1, v=6)
i=2    0    6   10   16   16   16  (item 1: w=2, v=10)
i=3    0    6   10   16   18   22  (item 2: w=3, v=12)

Answer: dp[3][5] = 22 (take items with w=2,v=10 and w=3,v=12)
```

---

## Example 6: Longest Common Subsequence (2D String DP)

### Problem
Find the length of the longest common subsequence between two strings.

Example: text1 = "abcde", text2 = "ace" → Output: 3 ("ace")

### 🧠 Thinking Process

**Step 1**: Is this DP?
- Asks for longest ✅
- Subsequence problem ✅
- Two strings → 2D DP

**Step 2**: Define State
- State: `(i, j)` where i = index in text1, j = index in text2
- `dp[i][j]` = LCS length for text1[0...i) and text2[0...j)

**Step 3**: Recurrence Relation

Think: "Compare characters at positions i and j"

```
if text1[i-1] == text2[j-1]:
    dp[i][j] = dp[i-1][j-1] + 1  # Match! Extend LCS
else:
    dp[i][j] = max(dp[i-1][j], dp[i][j-1])  # Skip one character
```

**Step 4**: Base Cases
```
dp[0][j] = 0  # Empty text1, LCS is 0
dp[i][0] = 0  # Empty text2, LCS is 0
```

### Solution

```python
def longestCommonSubsequence(text1, text2):
    """
    Time: O(m * n) where m, n are lengths
    Space: O(m * n)
    
    Classic 2D DP for string matching
    """
    m, n = len(text1), len(text2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if text1[i-1] == text2[j-1]:
                # Characters match
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                # Take max of skipping either character
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])
    
    return dp[m][n]

# Test
text1 = "abcde"
text2 = "ace"
print(longestCommonSubsequence(text1, text2))  # 3

text1 = "abc"
text2 = "abc"
print(longestCommonSubsequence(text1, text2))  # 3

text1 = "abc"
text2 = "def"
print(longestCommonSubsequence(text1, text2))  # 0
```

### Visual Trace
```
text1 = "abcde"
text2 = "ace"

      ""  a  c  e
 ""    0  0  0  0
 a     0  1  1  1
 b     0  1  1  1
 c     0  1  2  2
 d     0  1  2  2
 e     0  1  2  3

LCS = "ace" with length 3
```

---

## Practice Problems with Solutions

### Problem 1: House Robber

**Problem**: You're a robber planning to rob houses along a street. Each house has money, but you can't rob adjacent houses (alarm will trigger). Find maximum money you can rob.

Example: houses = [2, 7, 9, 3, 1] → Output: 12 (rob houses 0, 2, 4)

```python
def rob(nums):
    """
    🧠 Thinking:
    State: dp[i] = max money robbing up to house i
    Recurrence: dp[i] = max(dp[i-1], dp[i-2] + nums[i])
                        (skip house i OR rob it)
    Base: dp[0] = nums[0], dp[1] = max(nums[0], nums[1])
    
    Time: O(n)
    Space: O(1)
    """
    if not nums:
        return 0
    if len(nums) == 1:
        return nums[0]
    
    prev2 = nums[0]
    prev1 = max(nums[0], nums[1])
    
    for i in range(2, len(nums)):
        current = max(prev1, prev2 + nums[i])
        prev2 = prev1
        prev1 = current
    
    return prev1

# Test
print(rob([2, 7, 9, 3, 1]))  # 12
print(rob([1, 2, 3, 1]))     # 4
```

---

### Problem 2: Unique Paths

**Problem**: A robot is on an m x n grid. It can only move right or down. How many unique paths are there to reach bottom-right from top-left?

```python
def uniquePaths(m, n):
    """
    🧠 Thinking:
    State: dp[i][j] = number of paths to reach cell (i,j)
    Recurrence: dp[i][j] = dp[i-1][j] + dp[i][j-1]
                          (from top + from left)
    Base: dp[0][j] = 1 (one path along top row)
          dp[i][0] = 1 (one path along left column)
    
    Time: O(m * n)
    Space: O(n) - space optimized
    """
    # Space optimized: only keep one row
    dp = [1] * n
    
    for i in range(1, m):
        for j in range(1, n):
            dp[j] = dp[j] + dp[j-1]
    
    return dp[n-1]

# Test
print(uniquePaths(3, 7))  # 28
print(uniquePaths(3, 2))  # 3
```

---

### Problem 3: Word Break

**Problem**: Given a string s and a dictionary of words, determine if s can be segmented into space-separated dictionary words.

Example: s = "leetcode", wordDict = ["leet", "code"] → True

```python
def wordBreak(s, wordDict):
    """
    🧠 Thinking:
    State: dp[i] = True if s[0:i] can be segmented
    Recurrence: dp[i] = True if there exists j where:
                        dp[j] = True AND s[j:i] in wordDict
    Base: dp[0] = True (empty string can be segmented)
    
    Time: O(n^2 * m) where m is max word length
    Space: O(n)
    """
    n = len(s)
    dp = [False] * (n + 1)
    dp[0] = True  # Base case
    
    word_set = set(wordDict)  # For O(1) lookup
    
    for i in range(1, n + 1):
        for j in range(i):
            # Check if s[0:j] can be segmented
            # AND s[j:i] is a valid word
            if dp[j] and s[j:i] in word_set:
                dp[i] = True
                break
    
    return dp[n]

# Test
print(wordBreak("leetcode", ["leet", "code"]))  # True
print(wordBreak("applepenapple", ["apple", "pen"]))  # True
print(wordBreak("catsandog", ["cats", "dog", "sand", "and", "cat"]))  # False
```

---

### Problem 4: Edit Distance (Levenshtein Distance)

**Problem**: Find minimum operations (insert, delete, replace) to convert word1 to word2.

Example: word1 = "horse", word2 = "ros" → Output: 3

```python
def minDistance(word1, word2):
    """
    🧠 Thinking:
    State: dp[i][j] = min operations to convert word1[0:i] to word2[0:j]
    Recurrence:
        if word1[i-1] == word2[j-1]:
            dp[i][j] = dp[i-1][j-1]  # No operation needed
        else:
            dp[i][j] = 1 + min(
                dp[i-1][j],      # delete from word1
                dp[i][j-1],      # insert to word1
                dp[i-1][j-1]     # replace
            )
    Base: dp[0][j] = j (insert j characters)
          dp[i][0] = i (delete i characters)
    
    Time: O(m * n)
    Space: O(m * n)
    """
    m, n = len(word1), len(word2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    # Base cases
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if word1[i-1] == word2[j-1]:
                dp[i][j] = dp[i-1][j-1]
            else:
                dp[i][j] = 1 + min(
                    dp[i-1][j],      # delete
                    dp[i][j-1],      # insert
                    dp[i-1][j-1]     # replace
                )
    
    return dp[m][n]

# Test
print(minDistance("horse", "ros"))  # 3
print(minDistance("intention", "execution"))  # 5
```

---

### Problem 5: Palindromic Substrings

**Problem**: Count how many palindromic substrings are in a string.

Example: s = "aaa" → Output: 6 ("a", "a", "a", "aa", "aa", "aaa")

```python
def countSubstrings(s):
    """
    🧠 Thinking:
    State: dp[i][j] = True if s[i:j+1] is palindrome
    Recurrence:
        dp[i][j] = (s[i] == s[j]) AND dp[i+1][j-1]
    Base: dp[i][i] = True (single character)
          dp[i][i+1] = (s[i] == s[i+1]) (two characters)
    
    Time: O(n^2)
    Space: O(n^2)
    """
    n = len(s)
    dp = [[False] * n for _ in range(n)]
    count = 0
    
    # Every single character is a palindrome
    for i in range(n):
        dp[i][i] = True
        count += 1
    
    # Check for length 2
    for i in range(n - 1):
        if s[i] == s[i + 1]:
            dp[i][i + 1] = True
            count += 1
    
    # Check for lengths 3 and above
    for length in range(3, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            if s[i] == s[j] and dp[i + 1][j - 1]:
                dp[i][j] = True
                count += 1
    
    return count

# Alternative: Expand around center (more intuitive)
def countSubstrings_expand(s):
    """
    Time: O(n^2)
    Space: O(1)
    
    For each possible center, expand outward
    """
    def expand_around_center(left, right):
        count = 0
        while left >= 0 and right < len(s) and s[left] == s[right]:
            count += 1
            left -= 1
            right += 1
        return count
    
    result = 0
    for i in range(len(s)):
        # Odd length palindromes (single center)
        result += expand_around_center(i, i)
        # Even length palindromes (two centers)
        result += expand_around_center(i, i + 1)
    
    return result

# Test
print(countSubstrings("aaa"))  # 6
print(countSubstrings("abc"))  # 3
```

---

## Common Pitfalls and Tips

### ❌ Pitfall 1: Wrong State Definition
**Problem**: State doesn't capture all necessary information

**Example**: In Knapsack, only tracking capacity without tracking which items considered

**Fix**: Think carefully: "What information uniquely identifies a subproblem?"

---

### ❌ Pitfall 2: Incorrect Base Cases
**Problem**: Not initializing base cases properly

**Example**: Forgetting dp[0] = 0 in coin change

**Fix**: Always ask: "What's the answer for the simplest case?"

---

### ❌ Pitfall 3: Wrong Loop Order in Space Optimization
**Problem**: Overwriting values you still need

**Example**: In 0/1 Knapsack 1D, iterating capacity forward instead of backward

**Fix**: Draw out a small example and trace through manually

---

### ❌ Pitfall 4: Off-by-One Errors
**Problem**: Index confusion between dp array and input array

**Fix**: Be consistent with 0-indexed or 1-indexed throughout

---

### ✅ Tip 1: Start with Recursion
Write the recursive solution first, even if inefficient. It helps you understand the problem structure.

---

### ✅ Tip 2: Draw It Out
For 2D DP, draw a small table and fill it by hand. This reveals the pattern.

---

### ✅ Tip 3: Verify with Examples
Test your recurrence relation on small inputs manually before coding.

---

### ✅ Tip 4: Common Initialization Values
- **Minimum problems**: Initialize with `float('inf')`
- **Maximum problems**: Initialize with `float('-inf')` or 0
- **Counting problems**: Initialize with 0
- **Boolean problems**: Initialize with False

---

### ✅ Tip 5: Space Optimization Patterns
- **1D → O(1)**: If dp[i] only depends on dp[i-1] and dp[i-2]
- **2D → 1D**: If dp[i][j] only depends on dp[i-1][...] (previous row)

---

## Summary: Your DP Toolkit

### The Checklist
When you see a problem:

1. ✅ Does it ask for optimization/counting/possibility?
2. ✅ Can it be broken into subproblems?
3. ✅ Do subproblems overlap?

If yes to all → It's probably DP!

### The Process
1. Define the state
2. Write the recurrence
3. Identify base cases
4. Choose implementation (top-down vs bottom-up)
5. Code it up
6. Optimize space if needed

### The Patterns to Remember
- **Linear DP**: Fibonacci, Climbing Stairs, House Robber
- **2D Grid**: Unique Paths, Minimum Path Sum
- **Subsequence**: LIS, LCS
- **Knapsack**: 0/1 Knapsack, Subset Sum
- **String DP**: Edit Distance, Word Break

### Practice Strategy
1. Start with easy problems (Fibonacci, Climbing Stairs)
2. Master one pattern at a time
3. Do 5-10 problems per pattern
4. Review and understand WHY the solution works
5. Try to solve problems multiple ways (top-down, bottom-up, space-optimized)

---

## Additional Resources

### Where to Practice
1. **LeetCode**: Filter by "Dynamic Programming" tag
2. **Start with**: Easy → Medium → Hard
3. **Focus on**: Understanding patterns, not memorizing solutions

### Recommended Problem Sequence
1. Fibonacci Numbers
2. Climbing Stairs
3. House Robber
4. Coin Change
5. Longest Increasing Subsequence
6. 0/1 Knapsack
7. Unique Paths
8. Longest Common Subsequence
9. Edit Distance
10. Word Break

---

**Remember**: DP is a skill that improves with practice. Don't get discouraged if it feels hard at first. Focus on understanding one problem deeply rather than solving many problems superficially.

**Key Insight**: Once you recognize the pattern, DP problems become much easier. Most interview DP problems are variations of 5-6 core patterns.

Good luck! 🚀
