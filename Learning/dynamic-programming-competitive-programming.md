# Dynamic Programming for Competitive Programming: Concepts, Patterns, and Tricks

A practical, contest-oriented guide to designing, optimizing, and debugging DP solutions. Includes conceptual checklists, common patterns, optimization techniques, and concise templates.

- Who is this for: Competitive programmers (ICPC/Codeforces/AtCoder/CSES/etc.).
- Languages: Concepts are language-agnostic; templates show C++ and Python where concise.
- Goal: Move from "I think this is DP" to a fast, correct, optimized solution.

---

## 1) Mental Model

Dynamic Programming (DP) = optimal substructure + overlapping subproblems.

Typical steps:
1. Define the problem you want DP to answer (value, count, boolean, min/max, expected value, etc.).
2. Choose the state(s) that uniquely capture a subproblem.
3. Write the recurrence/transition between states.
4. Identify base cases and initialization.
5. Choose evaluation order (top-down memo vs bottom-up order).
6. Analyze complexity and memory; optimize if needed (space/time tricks).
7. Reconstruct the solution (optional but common in contests).

Success criteria:
- States are minimal but sufficient.
- Transition uses only previously solved subproblems (acyclic dependency in bottom-up; recursion with memo otherwise).
- Complexity fits within constraints; memory fits too.

---

## 2) Designing States (What to Remember)

- Minimality: Store only what future transitions need (index, remaining capacity, mask, parity, last character, modulo remainder, etc.).
- Dimensions: The number of independent choices often equals DP dimensions.
- Encodings: Use bitmasks for subsets (n ≤ ~22), remainders for divisibility, compressed coordinates for large indices.
- Granularity: For strings/sequences, indices define intervals (`l..r`), prefixes (`i`), suffixes, or both (`i, j`).
- Count vs optimize: If counting, often modulo arithmetic; if optimizing, use +/- INF for init.

Checklist:
- What decision is made at this subproblem?
- Which prefix/interval/subset have I processed?
- What context from the past affects future choices (last color, last chosen position, direction)?
- Can I drop any part of the context without breaking optimality?

---

## 3) Top-Down vs Bottom-Up

- Top-Down (memoized recursion): fast to write, natural for complex states; beware recursion limits and stack.
- Bottom-Up (iterative): deterministic order, no recursion limit, often easier to optimize memory and constant factors.
- Space optimization: If `dp[i]` depends only on `i-1` (or a fixed window), roll arrays.

Python memo pattern:
```python
from functools import lru_cache

@lru_cache(maxsize=None)
def f(i, j, tight, lead):
    # ... transitions ...
    return ans
```

C++ bottom-up init:
```cpp
const long long INF = (1LL<<60);
vector<long long> dp(n+1, INF);
dp[0] = 0; // base case
for (int i = 1; i <= n; ++i) {
    // transitions using smaller indices
}
```

---

## 4) Reconstructing Answers

Store parent info or choices:
- Keep `parent[i]` or `(prev_state, decision)`.
- For 2D, store `par[i][j]`.
- For LIS patience sorting, also keep predecessors to reconstruct sequence.

```cpp
vector<int> dp(n, 1), par(n, -1);
int best = 0, bi = 0;
for (int i = 0; i < n; ++i) {
    for (int j = 0; j < i; ++j) if (a[j] < a[i] && dp[j]+1 > dp[i]) {
        dp[i] = dp[j]+1; par[i] = j;
    }
    if (dp[i] > best) best = dp[i], bi = i;
}
vector<int> seq; for (int x = bi; x != -1; x = par[x]) seq.push_back(a[x]);
reverse(seq.begin(), seq.end());
```

---

## 5) 1D DP Patterns

Common shapes:
- Prefix DP: `dp[i]` depends on `dp[i-1]` (Kadane’s algorithm for max subarray).
- Counting DP: ways to form sum i by coins/steps.
- Knapsack family: 0/1 vs Unbounded vs Bounded; loop orders matter.
- LIS and variants: O(n^2) DP; O(n log n) patience for value only; O(n log n) + parent for reconstruction.

0/1 Knapsack (1D optimization):
```cpp
// weight w[i], value v[i], capacity W
auto knap01 = [&](){
    vector<long long> dp(W+1, 0);
    for (int i = 0; i < n; ++i) {
        for (int c = W; c >= w[i]; --c) {
            dp[c] = max(dp[c], dp[c - w[i]] + v[i]);
        }
    }
    return dp[W];
};
```

Unbounded Knapsack:
```cpp
for (int i = 0; i < n; ++i)
  for (int c = w[i]; c <= W; ++c)
    dp[c] = max(dp[c], dp[c - w[i]] + v[i]);
```

Coin Change (count combinations):
```cpp
vector<long long> dp(S+1, 0);
dp[0] = 1;
for (int coin: coins)
  for (int s = coin; s <= S; ++s)
    dp[s] = (dp[s] + dp[s-coin]) % MOD; // order: coin outer = combinations
```

Coin Change (count permutations): iterate sum outer, coins inner.

Kadane (max subarray sum):
```cpp
long long best = LLONG_MIN, cur = 0;
for (long long x: a) {
  cur = max(x, cur + x);
  best = max(best, cur);
}
```

---

## 6) Strings and Sequences (2D DP)

- LCS (Longest Common Subsequence): `dp[i][j] = 1 + dp[i-1][j-1]` if match else `max(dp[i-1][j], dp[i][j-1])`.
- LCSubstring: if match `dp[i][j] = dp[i-1][j-1] + 1` else 0.
- Edit Distance: `dp[i][j] = 1 + min(ins, del, sub)`.
- Palindromic Subsequence: `dp[l][r] = dp[l+1][r-1] + 2` if equal else `max(dp[l+1][r], dp[l][r-1])`.
- Palindromic Substring count: expand centers or `dp[l][r]` boolean.

Example (Edit Distance, iterative):
```cpp
int n = a.size(), m = b.size();
vector<vector<int>> dp(n+1, vector<int>(m+1));
for (int i = 0; i <= n; ++i) dp[i][0] = i;
for (int j = 0; j <= m; ++j) dp[0][j] = j;
for (int i = 1; i <= n; ++i)
  for (int j = 1; j <= m; ++j)
    dp[i][j] = (a[i-1]==b[j-1]) ? dp[i-1][j-1]
                                 : 1 + min({dp[i-1][j], dp[i][j-1], dp[i-1][j-1]});
```

---

## 7) Grid DP

- Count paths on grid with obstacles: `dp[i][j] = dp[i-1][j] + dp[i][j-1]` (mod).
- Minimum path sum with right/down moves.
- With costs and window constraints, sometimes a monotonic deque can optimize row/column transitions.

Space optimization: keep only previous row/column.

---

## 8) Interval DP

Solve problems where decisions split or merge intervals:
- Matrix Chain Multiplication
- Stone merging / optimal merge pattern
- Min triangulation of polygon
- Palindrome partitioning

General form:
```
dp[l][r] = min over k in (l..r-1) of dp[l][k] + dp[k+1][r] + cost(l,r)
```

Divide & Conquer Optimization (for `dp[i][j] = min_k<j { dp[i-1][k] + C(k, j) }`):
- Requirements: `argmin` is monotonic: `opt[i][j] <= opt[i][j+1]`.
- Complexity: `O(n log n)` or `O(nk log n)` depending on dims.

Template (1D stage transitions):
```cpp
void compute(int i, int L, int R, int optL, int optR) {
  if (L > R) return;
  int mid = (L + R) >> 1;
  pair<long long,int> best = {LLONG_MAX, -1};
  for (int k = optL; k <= min(mid, optR); ++k) {
    long long cand = dp[i-1][k] + C(k, mid);
    if (cand < best.first) best = {cand, k};
  }
  dp[i][mid] = best.first;
  int opt = best.second;
  compute(i, L, mid-1, optL, opt);
  compute(i, mid+1, R, opt, optR);
}
```

Knuth Optimization (for `dp[l][r]`):
- Form: `dp[l][r] = min_{k in [l, r-1]} dp[l][k] + dp[k+1][r] + w(l,r)`.
- Conditions: quadrangle inequality + monotone opt (`opt[l][r-1] <= opt[l][r] <= opt[l+1][r]`).
- Complexity: reduces from `O(n^3)` to `O(n^2)`.

---

## 9) DP on Trees

- Subtree DP: compute values from children to parent (post-order).
- Rerooting DP: compute answers for all roots by combining prefix/suffix of children contributions.
- Tree knapsack: capacity along edges or per node.

Tree DP skeleton (subtree size):
```cpp
vector<vector<int>> g(n);
vector<int> sub(n,1);
function<void(int,int)> dfs = [&](int u, int p){
  for (int v: g[u]) if (v!=p){
    dfs(v,u);
    sub[u] += sub[v];
  }
};
```

Rerooting idea:
1. First DFS: compute `dp_down[u]` using children.
2. Second DFS: propagate `dp_all[u]` to children using parent contribution via prefix/suffix.

---

## 10) DP on DAGs and General Graphs

- DAG longest path / path counting: topo order DP.
- With cycles: compress SCCs to DAG, then DP.
- Shortest path with non-negative edges is Dijkstra (not DP), but DP-like on DAG.

Topo DP skeleton:
```cpp
vector<int> topo = topo_order(g);
vector<long long> dp(n, -INF);
dp[src] = 0;
for (int u: topo)
  for (auto [v,w]: g[u])
    dp[v] = max(dp[v], dp[u] + w);
```

---

## 11) Bitmask DP (Subsets)

Use when `n ≤ 20..22` (sometimes 25 with bit tricks).
- TSP: `dp[mask][i]` = min cost ending at `i` having visited `mask`.
- Assignment: `dp[mask]` = min cost assigning first `popcount(mask)` jobs to set `mask`.
- Set/Subset DP (SOS DP) to aggregate over subsets/supersets.

TSP core transition:
```cpp
for (int mask = 1; mask < (1<<n); ++mask)
  for (int u = 0; u < n; ++u) if (mask & (1<<u))
    for (int v = 0; v < n; ++v) if (!(mask & (1<<v)))
      dp[mask | (1<<v)][v] = min(dp[mask | (1<<v)][v], dp[mask][u] + w[u][v]);
```

SOS DP (subset sums over masks):
```cpp
// f[mask] = sum of a[sub] for all sub ⊆ mask
for (int bit = 0; bit < K; ++bit)
  for (int mask = 0; mask < (1<<K); ++mask)
    if (mask & (1<<bit)) f[mask] += f[mask ^ (1<<bit)];
```

---

## 12) Digit DP

Count numbers in [0..N] with digit constraints.
State:
- `pos`: digit index (from most significant to least).
- `tight`: whether prefix equals N’s prefix.
- `lead`: leading zeros allowed.
- Extra: remainder, last digit, digit used mask, etc.

Skeleton:
```python
from functools import lru_cache

digits = list(map(int, str(N)))

@lru_cache(None)
def dfs(pos, tight, lead, rem):
    if pos == len(digits):
        return int(rem == 0)
    hi = digits[pos] if tight else 9
    ans = 0
    for d in range(0, hi+1):
        ans += dfs(pos+1, tight and d==hi, lead and d==0, (rem*10 + d)%M)
    return ans
```

Tips:
- Work with strings for easy digit access.
- Consider `lead` carefully when constraints ignore leading zeros.
- Memoization table size ~ positions × tight(2) × lead(2) × extras.

---

## 13) Expected Value / Probability DP

- Use linearity of expectation when possible.
- For Markov-like transitions: `E[state] = constant + sum(p * E[next])`.
- Solve by DP if acyclic; otherwise sometimes requires equations/gaussian elimination, or transform to absorbing states.
- Modular expected values: use modular inverse for division by probabilities.

Example (expected steps until exit in DAG-like transitions) is a direct DP in topo order.

---

## 14) Optimization Techniques and Tricks

- Space Rolling: `dp[i]` only depends on `i-1` → keep 2 rows or 1 vector.
- Prefix/Suffix Precomputation: to compute range-based transitions quickly.
- Monotonic Queue Optimization: when `dp[i] = min_{j in [i-k, i]} (dp[j] + g(j) - h(i))` with `g` monotone—maintain deque of candidate indices by slope-like comparisons.
- Divide & Conquer Optimization: for `dp[i][j] = min_k dp[i-1][k] + C(k,j)` with monotone `opt`.
- Knuth Optimization: for interval DPs with specific convexity/quadrangle conditions.
- Convex Hull Trick (CHT): minimize `m*x + b` over lines, x processed in monotone order (or Li Chao tree for arbitrary order). Great for `dp[i] = min_j (dp[j] + m_j * x_i + b_j)`.
- Li Chao Tree: dynamic CHT supporting arbitrary x insertion/query in `O(log X)`.
- Bitset Optimization:
  - Subset sum / 0-1 knapsack: `bitset` shifts and OR reduce complexity by 64×.
  - Example: `bs |= (bs << w)`; answer is any set bit ≤ W.
- Meet-in-the-Middle (MITM): for subset problems (n ≈ 30..40) split set in half, enumerate each side, sort and two-pointer/binary search to combine. Not DP, but a go-to alternative.
- WQS Binary Search: convert constrained optimization to penalized DP; binary search penalty λ, check feasibility or compute score.
- Coordinate Compression: shrink large coordinates to manageable indices for DP arrays.
- Topological Ordering: enforce correct DP order for DAG-like dependencies.
- Modulo Care: do `% MOD` at additions; keep negatives in range with `(x%MOD+MOD)%MOD`.

---

## 15) Implementation Patterns

- INF constants: `const long long INF = 4e18; const int INF32 = 1e9;`.
- Memory: Prefer `vector` over large VLA; reuse buffers in multiple tests.
- Initialization: For min DP, fill with +INF then set bases; for max DP, -INF.
- Loop order correctness (critical in knapsacks).
- Recursion depth: increase stack (Py: `sys.setrecursionlimit`), or convert to iterative.
- Hash maps vs arrays: arrays are faster when indexable; use `unordered_map`/`dict` for sparse states.
- I/O speed (C++ `ios::sync_with_stdio(false); cin.tie(nullptr);`).

Python speed tips:
- Use local variables in hot loops; avoid attribute lookups.
- Prefer arrays (`list`/`array`/`numpy` not allowed on some judges) carefully.
- PyPy may be faster for heavy pure-Python code.

---

## 16) Edge Cases and Debugging Checklist

- Base cases initialized? `dp[0]`, empty strings, zero capacity, single-element intervals.
- Off-by-one in indices (`i-1`, `l..r` inclusive/exclusive).
- Order of transitions (0/1 vs unbounded knapsack loops!).
- Overflow (use 64-bit; consider MOD if counting).
- Negative cycles (if graph-like; not DP unless DAG).
- Multiple test cases: reset DP properly each test.
- Reconstruction: track parents consistently; beware ties.
- Time/Mem: estimate `states × transitions_per_state` and bytes per state.

Debugging tools:
- Print small DP tables for tiny inputs.
- Assert invariants (monotonicity of opt, bounds on states).
- Start with top-down to validate recurrence; then port to bottom-up if needed.

---

## 17) Quick Reference (By Pattern)

- 0/1 Knapsack: `O(nW)`; reverse capacity loop.
- Unbounded Knapsack: `O(nW)`; forward capacity loop.
- Subset Sum (bitset): `O(W/64 * n)`.
- LIS: `O(n log n)` with patience; `O(n^2)` DP is OK for n ≤ 2000.
- LCS/Edit Distance: `O(nm)`.
- Interval DP: `O(n^3)` naive → `O(n^2)` with Knuth if applicable.
- Bitmask DP (TSP): `O(n^2 2^n)`.
- Digit DP: `O(pos × tight × lead × extras)` ~ `20 × 2 × 2 × extras`.
- Tree DP: `O(n)` or `O(n log n)` depending on combine op.
- D&C Optimization: `O(k n log n)`.
- CHT/Li Chao: `O(log n)` per op; x monotone allows deque trick.

---

## 18) Small Templates (Copy-Ready)

Boolean DP (subset sum) with bitset:
```cpp
int W; vector<int> w(n);
bitset<100001> bs; bs[0] = 1; // adjust max W
for (int x: w) bs |= (bs << x);
bool ok = bs[W];
```

Rerooting DP (pattern):
```cpp
// dp_down[u]: from children to u
// dp_all[u]: answer using u as root
vector<vector<int>> g(n);
vector<long long> dp_down(n), dp_all(n);

function<void(int,int)> dfs1 = [&](int u, int p){
  dp_down[u] = 1; // sample combine
  for (int v: g[u]) if (v!=p){
    dfs1(v,u);
    dp_down[u] += dp_down[v];
  }
};

function<void(int,int)> dfs2 = [&](int u, int p){
  long long pref = 0; // compute contributions excluding a child via prefix/suffix
  // ... fill dp_all[u] ...
  for (int v: g[u]) if (v!=p){
    // push parent contribution to child v
    dfs2(v,u);
  }
};
```

Convex Hull Trick (deque, monotone m and x):
```cpp
struct Line{ long long m,b; double x; }; // x: intersection with next
// maintain lower hull for minima; insert slopes m in increasing order;
// query x in increasing order. Implement with pointer or deque.
```

Digit DP minimal:
```python
from functools import lru_cache
s = str(N)
@lru_cache(None)
def f(i, tight, lead):
  if i == len(s): return 1 # or condition
  lo, hi = 0, (int(s[i]) if tight else 9)
  ans = 0
  for d in range(lo, hi+1):
    ans += f(i+1, tight and d==hi, lead and d==0)
  return ans
```

D&C Optimization stub:
```cpp
for (int i = 1; i <= K; ++i)
  compute(i, 1, n, 1, n);
```

---

## 19) Practice Directions (Optional)

- Solve each pattern’s basic problem first, then add one twist (constraints, modulo, reconstruction).
- Implement at least one solution each with: top-down, bottom-up, and a space-optimized variant.
- Try an optimization (D&C, Knuth, CHT, bitset) on a problem where it applies.

---

## 20) Final Notes

- DP is about making the future independent of the past beyond your state.
- If transitions feel tangled, your state is probably too big or not aligned with the decision order.
- Build small, verify on toy inputs, and only then push to the full constraints.
