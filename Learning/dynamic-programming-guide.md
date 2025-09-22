# Dynamic Programming Complete Guide

## Table of Contents
1. [Introduction to Dynamic Programming](#introduction)
2. [Core Principles](#core-principles)
3. [Types of DP Problems](#types-of-dp-problems)
4. [Common Patterns and Techniques](#patterns)
5. [Classic Problems with Solutions](#classic-problems)
6. [Memory Tricks and Pattern Recognition](#memory-tricks)
7. [Practice Strategy](#practice-strategy)

## Introduction to Dynamic Programming {#introduction}

Dynamic Programming (DP) is an algorithmic technique used to solve optimization problems by breaking them down into simpler subproblems. It stores the results of subproblems to avoid redundant calculations.

### Key Characteristics:
- **Optimal Substructure**: The optimal solution contains optimal solutions to subproblems
- **Overlapping Subproblems**: The same subproblems are solved multiple times
- **Memoization**: Store results to avoid recalculation

### When to Use DP:
1. The problem can be broken down into subproblems
2. Subproblems overlap (same calculations repeated)
3. Optimal solution can be constructed from optimal solutions of subproblems

---

## Core Principles {#core-principles}

### 1. Memoization (Top-Down Approach)
Start with the original problem and recursively break it down, storing results.

```python
# Example: Fibonacci with memoization
def fibonacci_memo(n, memo={}):
    if n in memo:
        return memo[n]
    if n <= 1:
        return n
    memo[n] = fibonacci_memo(n-1, memo) + fibonacci_memo(n-2, memo)
    return memo[n]
```

### 2. Tabulation (Bottom-Up Approach)
Start with the smallest subproblems and build up to the original problem.

```python
# Example: Fibonacci with tabulation
def fibonacci_tab(n):
    if n <= 1:
        return n
    dp = [0] * (n + 1)
    dp[1] = 1
    for i in range(2, n + 1):
        dp[i] = dp[i-1] + dp[i-2]
    return dp[n]
```

**Memory Trick**: 
- **Memoization = "Memo-ry" = Remember results as you go DOWN**
- **Tabulation = "Tab-le" = Fill up a table from BOTTOM to TOP**

---

## Types of DP Problems {#types-of-dp-problems}

### 1. Linear DP
Problems where state depends on previous states in a linear fashion.

**Pattern**: `dp[i] = f(dp[i-1], dp[i-2], ...)`

**Examples**: Fibonacci, Climbing Stairs, House Robber

### 2. 2D DP
Problems involving two dimensions (usually involving two strings or arrays).

**Pattern**: `dp[i][j] = f(dp[i-1][j], dp[i][j-1], dp[i-1][j-1], ...)`

**Examples**: Edit Distance, Longest Common Subsequence, Unique Paths

### 3. Interval DP
Problems involving optimal ways to split intervals.

**Pattern**: `dp[i][j] = min/max(dp[i][k] + dp[k+1][j] + cost) for k in range(i, j)`

**Examples**: Matrix Chain Multiplication, Palindrome Partitioning

### 4. Tree DP
Problems on tree structures.

**Pattern**: `dp[node] = f(dp[child1], dp[child2], ...)`

**Examples**: Diameter of Binary Tree, House Robber III

### 5. Bitmask DP
Problems involving subsets and combinations.

**Pattern**: `dp[mask] = optimal value for subset represented by mask`

**Examples**: Traveling Salesman Problem, Shortest Hamiltonian Path

---

## Common Patterns and Techniques {#patterns}

### Pattern 1: Decision Making (Take or Don't Take)

**When to use**: When you have choices at each step.

**Template**:
```python
def solve(i, ...):
    if base_case:
        return result
    
    # Don't take current element
    option1 = solve(i+1, ...)
    
    # Take current element
    option2 = solve(i+1, ...) + value[i]
    
    return max(option1, option2)  # or min depending on problem
```

**Memory Trick**: "To be or not to be" - Shakespeare's choice dilemma

**Examples**: 
- 0/1 Knapsack
- House Robber
- Subset Sum

### Pattern 2: Unbounded Choices

**When to use**: When you can use elements multiple times.

**Template**:
```python
def solve(target):
    if target == 0:
        return 1  # or 0 depending on problem
    if target < 0:
        return 0
    
    result = 0
    for choice in choices:
        result += solve(target - choice)
    
    return result
```

**Memory Trick**: "All you can eat buffet" - unlimited choices

**Examples**:
- Coin Change
- Unbounded Knapsack
- Climbing Stairs (with variable steps)

### Pattern 3: String Matching

**When to use**: Comparing two strings/sequences.

**Template**:
```python
def solve(s1, s2, i, j):
    if i == len(s1) or j == len(s2):
        return base_value
    
    if s1[i] == s2[j]:
        return solve(s1, s2, i+1, j+1) + 1
    else:
        return max(solve(s1, s2, i+1, j), solve(s1, s2, i, j+1))
```

**Memory Trick**: "Dating app matching" - comparing profiles character by character

**Examples**:
- Longest Common Subsequence
- Edit Distance
- Wildcard Matching

### Pattern 4: Palindrome Problems

**When to use**: Finding optimal ways to make palindromes.

**Template**:
```python
def solve(s, i, j):
    if i >= j:
        return 0  # or 1 depending on problem
    
    if s[i] == s[j]:
        return solve(s, i+1, j-1)
    else:
        return 1 + min(solve(s, i+1, j), solve(s, i, j-1))
```

**Memory Trick**: "Mirror, mirror on the wall" - checking reflections from both ends

**Examples**:
- Longest Palindromic Subsequence
- Palindrome Partitioning
- Minimum Insertions to Make Palindrome

### Pattern 5: Grid Path Problems

**When to use**: Finding paths in 2D grids.

**Template**:
```python
def solve(grid, i, j):
    if i == m-1 and j == n-1:
        return grid[i][j]
    if i >= m or j >= n:
        return float('inf')  # or 0
    
    right = solve(grid, i, j+1)
    down = solve(grid, i+1, j)
    
    return grid[i][j] + min(right, down)
```

**Memory Trick**: "GPS navigation" - finding optimal routes on a map

**Examples**:
- Unique Paths
- Minimum Path Sum
- Dungeon Game

---

## Classic Problems with Solutions {#classic-problems}

### 1. Fibonacci Sequence

**Problem**: Find the nth Fibonacci number.

**Recurrence**: `F(n) = F(n-1) + F(n-2)`

**Memory Trick**: "Rabbit breeding" - each pair produces offspring after maturing

```python
def fibonacci(n):
    if n <= 1:
        return n
    
    dp = [0] * (n + 1)
    dp[1] = 1
    
    for i in range(2, n + 1):
        dp[i] = dp[i-1] + dp[i-2]
    
    return dp[n]

# Space optimized
def fibonacci_optimized(n):
    if n <= 1:
        return n
    
    prev2, prev1 = 0, 1
    for i in range(2, n + 1):
        current = prev1 + prev2
        prev2, prev1 = prev1, current
    
    return prev1
```

### 2. 0/1 Knapsack

**Problem**: Given items with weights and values, maximize value within weight capacity.

**Memory Trick**: "Packing for vacation" - choose items that give maximum value

```python
def knapsack(weights, values, capacity):
    n = len(weights)
    dp = [[0 for _ in range(capacity + 1)] for _ in range(n + 1)]
    
    for i in range(1, n + 1):
        for w in range(1, capacity + 1):
            # Don't take item i-1
            dp[i][w] = dp[i-1][w]
            
            # Take item i-1 if possible
            if weights[i-1] <= w:
                dp[i][w] = max(dp[i][w], 
                              dp[i-1][w - weights[i-1]] + values[i-1])
    
    return dp[n][capacity]

# Space optimized
def knapsack_optimized(weights, values, capacity):
    dp = [0] * (capacity + 1)
    
    for i in range(len(weights)):
        for w in range(capacity, weights[i] - 1, -1):
            dp[w] = max(dp[w], dp[w - weights[i]] + values[i])
    
    return dp[capacity]
```

### 3. Longest Common Subsequence (LCS)

**Problem**: Find the length of the longest common subsequence between two strings.

**Memory Trick**: "Finding common DNA sequences" - matching genetic patterns

```python
def lcs(text1, text2):
    m, n = len(text1), len(text2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if text1[i-1] == text2[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])
    
    return dp[m][n]

# With path reconstruction
def lcs_with_path(text1, text2):
    m, n = len(text1), len(text2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    # Fill DP table
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if text1[i-1] == text2[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])
    
    # Reconstruct LCS
    lcs = []
    i, j = m, n
    while i > 0 and j > 0:
        if text1[i-1] == text2[j-1]:
            lcs.append(text1[i-1])
            i -= 1
            j -= 1
        elif dp[i-1][j] > dp[i][j-1]:
            i -= 1
        else:
            j -= 1
    
    return dp[m][n], ''.join(reversed(lcs))
```

### 4. Edit Distance (Levenshtein Distance)

**Problem**: Find minimum operations to convert one string to another.

**Memory Trick**: "Text editor autocorrect" - fixing typos with minimum changes

```python
def edit_distance(word1, word2):
    m, n = len(word1), len(word2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    # Initialize base cases
    for i in range(m + 1):
        dp[i][0] = i  # Delete all characters
    for j in range(n + 1):
        dp[0][j] = j  # Insert all characters
    
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if word1[i-1] == word2[j-1]:
                dp[i][j] = dp[i-1][j-1]  # No operation needed
            else:
                dp[i][j] = 1 + min(
                    dp[i-1][j],     # Delete
                    dp[i][j-1],     # Insert
                    dp[i-1][j-1]    # Replace
                )
    
    return dp[m][n]
```

### 5. Coin Change

**Problem**: Find minimum coins needed to make a target amount.

**Memory Trick**: "Making change at a store" - using fewest coins possible

```python
def coin_change(coins, amount):
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0
    
    for coin in coins:
        for i in range(coin, amount + 1):
            dp[i] = min(dp[i], dp[i - coin] + 1)
    
    return dp[amount] if dp[amount] != float('inf') else -1

# Count number of ways
def coin_change_ways(coins, amount):
    dp = [0] * (amount + 1)
    dp[0] = 1
    
    for coin in coins:
        for i in range(coin, amount + 1):
            dp[i] += dp[i - coin]
    
    return dp[amount]
```

### 6. House Robber

**Problem**: Rob houses without robbing adjacent ones, maximize money.

**Memory Trick**: "Burglar's dilemma" - can't rob neighboring houses

```python
def rob(nums):
    if not nums:
        return 0
    if len(nums) == 1:
        return nums[0]
    
    dp = [0] * len(nums)
    dp[0] = nums[0]
    dp[1] = max(nums[0], nums[1])
    
    for i in range(2, len(nums)):
        dp[i] = max(dp[i-1], dp[i-2] + nums[i])
    
    return dp[-1]

# Space optimized
def rob_optimized(nums):
    if not nums:
        return 0
    
    prev2 = prev1 = 0
    for num in nums:
        current = max(prev1, prev2 + num)
        prev2, prev1 = prev1, current
    
    return prev1
```

### 7. Longest Increasing Subsequence

**Problem**: Find length of longest increasing subsequence.

**Memory Trick**: "Stock prices going up" - finding longest upward trend

```python
def lis(nums):
    if not nums:
        return 0
    
    dp = [1] * len(nums)
    
    for i in range(1, len(nums)):
        for j in range(i):
            if nums[j] < nums[i]:
                dp[i] = max(dp[i], dp[j] + 1)
    
    return max(dp)

# Optimized O(n log n) solution
def lis_optimized(nums):
    if not nums:
        return 0
    
    from bisect import bisect_left
    
    tails = []
    for num in nums:
        pos = bisect_left(tails, num)
        if pos == len(tails):
            tails.append(num)
        else:
            tails[pos] = num
    
    return len(tails)
```

### 8. Palindromic Substrings

**Problem**: Count number of palindromic substrings.

**Memory Trick**: "Mirror writing" - text that reads same forwards and backwards

```python
def count_palindromes(s):
    n = len(s)
    dp = [[False] * n for _ in range(n)]
    count = 0
    
    # Single characters are palindromes
    for i in range(n):
        dp[i][i] = True
        count += 1
    
    # Two character palindromes
    for i in range(n - 1):
        if s[i] == s[i + 1]:
            dp[i][i + 1] = True
            count += 1
    
    # Longer palindromes
    for length in range(3, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            if s[i] == s[j] and dp[i + 1][j - 1]:
                dp[i][j] = True
                count += 1
    
    return count

# Expand around centers approach
def count_palindromes_optimized(s):
    def expand_around_center(left, right):
        count = 0
        while left >= 0 and right < len(s) and s[left] == s[right]:
            count += 1
            left -= 1
            right += 1
        return count
    
    total = 0
    for i in range(len(s)):
        # Odd length palindromes
        total += expand_around_center(i, i)
        # Even length palindromes
        total += expand_around_center(i, i + 1)
    
    return total
```

---

## Memory Tricks and Pattern Recognition {#memory-tricks}

### 1. Problem Type Recognition

**Linear Problems** 🔄
- **Trigger Words**: "sequence", "array", "previous elements"
- **Memory Trick**: "Train cars in a line" - each car depends on previous ones
- **Examples**: Fibonacci, Climbing Stairs, House Robber

**Grid Problems** 🔲
- **Trigger Words**: "2D array", "paths", "grid", "matrix"
- **Memory Trick**: "Chess board movement" - can only move in certain directions
- **Examples**: Unique Paths, Minimum Path Sum

**String Problems** 📝
- **Trigger Words**: "two strings", "subsequence", "matching", "edit"
- **Memory Trick**: "DNA comparison" - comparing two genetic sequences
- **Examples**: LCS, Edit Distance, Wildcard Matching

**Decision Problems** 🤔
- **Trigger Words**: "choose", "select", "maximum", "optimal"
- **Memory Trick**: "Shopping cart decisions" - take item or leave it
- **Examples**: Knapsack, Subset Sum, Partition

### 2. State Design Mnemonics

**What information do I need to make a decision?**

- **Position**: Where am I in the problem? (index i)
- **Capacity**: What's my current limit? (remaining weight, budget)
- **Previous Choice**: What did I just do? (last element taken)
- **Target**: What am I trying to achieve? (sum, length)

**Memory Trick**: "GPS Navigation System"
- **Position**: Current location
- **Capacity**: Fuel remaining
- **Previous**: Last turn taken
- **Target**: Destination

### 3. Base Case Identification

**Ask yourself**: "When is the problem trivial?"

- **Empty input**: `if n == 0 or len(arr) == 0`
- **Single element**: `if n == 1`
- **Target reached**: `if sum == target`
- **Boundary exceeded**: `if i >= len(arr)`

**Memory Trick**: "Recipe cooking steps"
- No ingredients = nothing to cook (return 0)
- One ingredient = trivial recipe (return that ingredient)
- Goal achieved = dish ready (return success)

### 4. Transition Recognition Patterns

**Linear Transition**: Current state depends on previous states
```
dp[i] = f(dp[i-1], dp[i-2], ...)
```
**Memory**: "Domino effect" - each piece affects the next

**Choice Transition**: Current state depends on making optimal choices
```
dp[i] = max(choice1, choice2, choice3)
```
**Memory**: "Multiple choice test" - pick the best option

**Conditional Transition**: Depends on current element properties
```
if condition:
    dp[i][j] = dp[i-1][j-1]
else:
    dp[i][j] = dp[i-1][j] + dp[i][j-1]
```
**Memory**: "Traffic light logic" - different actions based on signal

### 5. Optimization Tricks

**Space Optimization Patterns**:

1. **Only need previous row/column**: Use 1D array
   - **Memory**: "Conveyor belt" - only current and previous matter

2. **Only need last few values**: Use variables
   - **Memory**: "Short term memory" - remember just essentials

3. **Process in reverse order**: Avoid overwriting needed values
   - **Memory**: "Undo button" - work backwards to avoid conflicts

### 6. Debugging DP Solutions

**Common Issues and Fixes**:

1. **Wrong Base Cases**
   - **Check**: Are trivial cases handled correctly?
   - **Memory**: "Foundation of a building" - must be solid

2. **Off-by-one Errors**
   - **Check**: Array bounds and loop ranges
   - **Memory**: "Fence post problem" - count posts, not gaps

3. **Wrong Transition Formula**
   - **Check**: Are all choices considered?
   - **Memory**: "All roads lead to Rome" - consider every path

4. **Overlapping vs Non-overlapping**
   - **Check**: Can same element be used multiple times?
   - **Memory**: "All-you-can-eat vs à la carte" - unlimited vs one-time

---

## Practice Strategy {#practice-strategy}

### Phase 1: Foundation Building (Week 1-2)
1. **Master Basic Patterns**:
   - Fibonacci variations
   - Simple array problems
   - Basic string problems

2. **Practice Problems**:
   - Climbing Stairs
   - Min Cost Climbing Stairs
   - House Robber
   - Maximum Subarray

### Phase 2: Pattern Recognition (Week 3-4)
1. **2D DP Problems**:
   - Unique Paths
   - Minimum Path Sum
   - Longest Common Subsequence

2. **Decision-based Problems**:
   - 0/1 Knapsack
   - Subset Sum
   - Partition Equal Subset Sum

### Phase 3: Advanced Patterns (Week 5-6)
1. **String DP**:
   - Edit Distance
   - Wildcard Matching
   - Regular Expression Matching

2. **Interval DP**:
   - Matrix Chain Multiplication
   - Palindrome Partitioning
   - Burst Balloons

### Phase 4: Optimization & Variants (Week 7-8)
1. **Space Optimization**:
   - Convert 2D solutions to 1D
   - Rolling array techniques

2. **Path Reconstruction**:
   - Store decisions for backtracking
   - Print actual solutions, not just optimal values

### Daily Practice Routine:
1. **Morning (30 mins)**: Solve 1-2 easy problems
2. **Evening (45 mins)**: Solve 1 medium problem
3. **Weekend (2 hours)**: Solve 1 hard problem and review patterns

### Problem-Solving Framework:
1. **Identify the pattern** (5 mins)
2. **Define state and transitions** (10 mins)
3. **Write recursive solution** (10 mins)
4. **Add memoization** (5 mins)
5. **Convert to tabulation** (10 mins)
6. **Optimize space if possible** (10 mins)

---

## Quick Reference Cheat Sheet

### Pattern Recognition Flowchart:
```
Is it about sequences/arrays? → Linear DP
Is it about 2 strings? → String DP
Is it about choosing items? → Decision DP
Is it about paths in grid? → Grid DP
Is it about intervals? → Interval DP
Is it about subsets? → Bitmask DP
```

### Common Recurrence Relations:
- **Fibonacci**: `F(n) = F(n-1) + F(n-2)`
- **Climbing Stairs**: `ways(n) = ways(n-1) + ways(n-2)`
- **Knapsack**: `dp[i][w] = max(dp[i-1][w], dp[i-1][w-weight] + value)`
- **LCS**: `dp[i][j] = dp[i-1][j-1] + 1 if match, else max(dp[i-1][j], dp[i][j-1])`
- **Edit Distance**: `dp[i][j] = min(insert, delete, replace) + 1`

### Space Complexity Patterns:
- **1D DP**: O(n) space
- **2D DP**: O(mn) space → Often reducible to O(min(m,n))
- **Rolling Array**: O(k) space where k is lookback distance

Remember: **Practice makes perfect!** Start with easier problems and gradually work your way up. Focus on understanding the patterns rather than memorizing solutions.
