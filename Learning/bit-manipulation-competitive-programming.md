# Bit Manipulation for Competitive Programming — Cheatsheet and Patterns

A practical, example‑driven guide to bit hacks, subset enumeration, DP with bitmasks, XOR tricks, and language built‑ins. Includes concise C++ and Python templates (plus Java/Rust tips) you can drop into solutions.

- Audience: ICPC/Codeforces/AtCoder/LeetCode contestants
- Scope: n ≤ ~22–25 for full mask DP; n ≤ ~20–23 for SOS DP in tight limits; larger n use bitset tricks or math

## 1) Operator basics

- AND: a & b — keep 1s present in both
- OR: a | b — keep 1s present in either
- XOR: a ^ b — keep 1s present in exactly one
- NOT: ~a — bitwise inversion (watch signed types)
- Shifts: a << k, a >> k — arithmetic vs logical depends on signedness (C++). Use unsigned for predictable logical shifts.

Bit i (0-based from LSB):
- Test: (x >> i) & 1
- Set: x | (1 << i)
- Clear: x & ~(1 << i)
- Toggle: x ^ (1 << i)

64-bit note (C/C++): use 1ULL << i to avoid overflow/UB when i ≥ 31.

Python note: ints are arbitrary precision; performance still matters.

## 2) Core idioms (must-know)

Let x > 0 be an integer unless noted.

- Remove lowest set bit: x & (x - 1)
- Isolate lowest set bit (lowbit): x & -x
- Is power of two: x > 0 && (x & (x - 1)) == 0
- Count set bits: popcount(x)
- Index of lowest set bit (ctz): ctz(x) = index of lowbit
- Index of highest set bit (floor log2): msb_index = bit_length(x) - 1
- Highest power of two ≤ x: 1 << (bit_length(x) - 1)
- Next power of two ≥ x: bit_ceil(x) (C++20) or round-up trick below
- Turn on all bits below MSB: y = x; y |= y >> 1; y |= y >> 2; y |= y >> 4; y |= y >> 8; y |= y >> 16; ...
- Round up to next power of two: bit_ceil = y + 1 (with y as above); handle x == 0 separately
- Turn on rightmost 0: x | (x + 1)
- Turn off rightmost 1: x & (x - 1) (same as “remove lowest set bit”)
- Parity (even/odd popcount): popcount(x) & 1

C++ snippets:
- popcount: __builtin_popcount(x), __builtin_popcountll(x)
- ctz: __builtin_ctz(x) (undefined for x == 0; guard)
- clz: __builtin_clz(x) (undefined for x == 0; guard)
- C++20 <bit>: std::popcount, std::countr_zero, std::countl_zero, std::bit_width, std::bit_floor, std::bit_ceil

Python snippets:
- popcount: x.bit_count()
- bit length: x.bit_length()
- ctz: (x & -x).bit_length() - 1 if x > 0 else undefined
- msb: 1 << (x.bit_length() - 1) if x > 0 else 0

## 3) Enumerating masks and bits

- Iterate all masks of size n (0..(1<<n)-1):
  - C++: for (int m = 0; m < (1<<n); ++m) { ... }
  - Py: for m in range(1 << n): ...

- Iterate set bits of a mask (fast):
  - C++:
    - for (int s = m; s; s &= s - 1) { int i = __builtin_ctz(s); /* bit index */ }
    - Or: while (s) { int b = s & -s; int i = __builtin_ctz(s); s ^= b; }
  - Py:
    - s = m
      while s:
          lsb = s & -s
          i = (s & -s).bit_length() - 1
          s ^= lsb

- Iterate all submasks of mask m:
  - C++: for (int sub = m; ; sub = (sub - 1) & m) { ... if (sub == 0) break; }
  - Py: sub = m;  while True: ...;  if sub == 0: break;  sub = (sub - 1) & m

- Iterate all supersets of m within n bits (use complement trick):
  - Iterate submasks of (~m) within n bits; sup = sub ^ ((1<<n) - 1)

- Iterate all k-bit masks among n bits (Gosper’s hack): see §5.

Complexities:
- All masks: O(2^n)
- All submasks of all masks: O(3^n)
- For fixed m, all submasks: O(2^{popcount(m)})

## 4) Subset DP and classic patterns

### 4.1 Traveling Salesman (TSP) DP
State: dp[mask][u] = min cost to end at u having visited exactly mask (mask includes u). Complexity O(n^2 2^n).

C++ (n ≤ 20):

// dist[u][v] given
const int INF = 1e9;
int N; // nodes
int FULL = 1<<N;
vector<vector<int>> dp(FULL, vector<int>(N, INF));
dp[1][0] = 0; // start at 0
for (int mask = 1; mask < FULL; ++mask) {
  for (int u = 0; u < N; ++u) if (mask & (1<<u)) {
    int cur = dp[mask][u]; if (cur >= INF) continue;
    for (int v = 0; v < N; ++v) if (!(mask & (1<<v))) {
      int nxt = mask | (1<<v);
      dp[nxt][v] = min(dp[nxt][v], cur + dist[u][v]);
    }
  }
}
int ans = INF;
for (int u = 0; u < N; ++u) ans = min(ans, dp[FULL-1][u] + dist[u][0]);

Python (use lists; consider PyPy and local arrays for speed):

# dist[u][v] given
INF = 10**18
N = len(dist)
FULL = 1 << N
dp = [[INF]*N for _ in range(FULL)]
dp[1][0] = 0
for mask in range(1, FULL):
    for u in range(N):
        if mask >> u & 1:
            cur = dp[mask][u]
            if cur >= INF: continue
            rem = ((1 << N) - 1) ^ mask
            v = rem
            while v:
                lsb = v & -v
                i = (lsb.bit_length() - 1)
                nxt = mask | (1 << i)
                cand = cur + dist[u][i]
                if cand < dp[nxt][i]:
                    dp[nxt][i] = cand
                v ^= lsb
ans = min(dp[FULL-1][u] + dist[u][0] for u in range(N))

### 4.2 Partition DP (submask enumeration)
Given f[S] computed from submasks A ⊂ S and B = S\A (like splitting S into two parts):

for (int S = 0; S < (1<<n); ++S) {
  for (int A = S; A; A = (A-1) & S) {
    int B = S ^ A;
    // relax using A and B
  }
}

### 4.3 Meet-in-the-middle with bitsets
Use 64-bit blocks or std::bitset to accelerate convolutions/DP or adjacency multiplication. Python’s int works as a dynamic bitset: row bitmask for adjacency; BFS frontier update via bitwise ops.

## 5) Gosper’s hack (next k-combination)

Generate the next integer with the same number of set bits (k) in lexicographic order.

C++ (unsigned):

uint64_t next_comb(uint64_t x) {
  uint64_t c = x & -x;
  uint64_t r = x + c;
  if (r == 0) return 0; // overflow: no next
  return (((r ^ x) >> 2) / c) | r;
}

Usage to iterate k-set-bit masks among n bits:

int n, k; // given
uint64_t x = (1ULL << k) - 1; // first k ones
uint64_t limit = 1ULL << n;
for (; x && x < limit; x = next_comb(x)) {
  // use x
}

Python:

def next_comb(x: int) -> int:
    c = x & -x
    r = x + c
    if r == 0:
        return 0
    return (((r ^ x) >> 2) // c) | r

## 6) SOS DP (Sum Over Subsets) — Zeta/Möbius transforms

Goal: For array F[mask], compute G[mask] = sum_{sub ⊆ mask} F[sub] in O(n·2^n).

C++:

int n; // up to ~22
int N = 1<<n;
vector<long long> G = F; // copy
for (int i = 0; i < n; ++i) {
  for (int mask = 0; mask < N; ++mask) {
    if (mask & (1<<i)) G[mask] += G[mask ^ (1<<i)];
  }
}

Inverse (Möbius): replace += with -= in same loops.

Common uses:
- Count-of-supersets/subsets queries
- DP transitions that aggregate over submasks
- Convolution over subset lattice

Python:

def sos_zeta(G, n):
    for i in range(n):
        for mask in range(1<<n):
            if mask & (1<<i):
                G[mask] += G[mask ^ (1<<i)]
    return G

def sos_mobius(G, n):
    for i in range(n):
        for mask in range(1<<n):
            if mask & (1<<i):
                G[mask] -= G[mask ^ (1<<i)]
    return G

## 7) XOR tricks and linear basis (Gaussian elimination over GF(2))

### 7.1 Prefix XOR
- Subarray XOR [l..r] = pref[r] ^ pref[l-1].
- Count subarrays with XOR = K using hashmap of prefix frequencies.

### 7.2 One/two unique numbers
- One unique, others twice: XOR of all gives the unique.
- Two uniques, others twice: XOR all to get t = a ^ b; isolate bit p = t & -t; partition by p and XOR within groups to recover a, b.

### 7.3 Max XOR subset (linear basis)

C++ (64-bit basis):

struct XorBasis {
  static constexpr int LOG = 60;
  long long b[LOG]{}; // b[i] has highest bit i
  void add(long long x) {
    for (int i = LOG-1; i >= 0; --i) if (x & (1LL<<i)) {
      if (!b[i]) { b[i] = x; return; }
      x ^= b[i];
    }
  }
  long long get_max() const {
    long long x = 0;
    for (int i = LOG-1; i >= 0; --i) x = max(x, x ^ b[i]);
    return x;
  }
  int rank() const {
    int r = 0; for (auto v: b) if (v) ++r; return r;
  }
};

Python:

class XorBasis:
    LOG = 60
    def __init__(self):
        self.b = [0]*self.LOG
    def add(self, x: int):
        for i in range(self.LOG-1, -1, -1):
            if x >> i & 1:
                if self.b[i] == 0:
                    self.b[i] = x
                    return
                x ^= self.b[i]
    def get_max(self) -> int:
        x = 0
        for i in range(self.LOG-1, -1, -1):
            x = max(x, x ^ self.b[i])
        return x
    def rank(self) -> int:
        return sum(1 for v in self.b if v)

Facts:
- Number of distinct XORs form a vector space of size 2^{rank}.
- To check if y is representable: try to reduce y by basis; if 0 remains, yes.

### 7.4 Fast Walsh–Hadamard Transform (FWHT) for XOR convolution
Convolves sequences under XOR in O(n log n) where n is power of two. Useful for subset XOR distribution.

C++ sketch (in-place):

void fwht(vector<long long>& a, bool inverse) {
  int n = a.size();
  for (int len = 1; 2*len <= n; len <<= 1) {
    for (int i = 0; i < n; i += 2*len) {
      for (int j = 0; j < len; ++j) {
        long long u = a[i+j];
        long long v = a[i+j+len];
        a[i+j] = u + v;
        a[i+j+len] = u - v;
      }
    }
  }
  if (inverse) {
    for (long long &x : a) x /= n;
  }
}

## 8) Bitsets for speed

- C++ std::bitset<N> is fixed-size at compile time; bitwise ops are vectorized/word-wise and very fast. Use to accelerate DP, transitive closure, maximum bipartite matching precomputation, etc.
- For dynamic size, use vector<uint64_t>, boost::dynamic_bitset, or libraries. Operations scale ~O(n/64).
- Python: integers serve as dynamic bitsets. Example: BFS frontier on an unweighted graph stored as bit-masks of neighbors; next_frontier = OR of adj[u] over u in frontier which can be computed as a sum of shifted masks or via bit tricks.

Example: count triangles via bitset intersections (C++):

long long triangles = 0;
for (int u = 0; u < n; ++u)
  for (int v = u+1; v < n; ++v)
    if (G[u][v]) triangles += (bitset_adj[u] & bitset_adj[v]).count();

## 9) Language built-ins and tips

### C++ (GCC/Clang)
- __builtin_popcount(unsigned), __builtin_popcountll(unsigned long long)
- __builtin_ctz / __builtin_ctzll (undefined for 0)
- __builtin_clz / __builtin_clzll (undefined for 0)
- __builtin_parity / __builtin_parityll
- Prefer unsigned types for shifts; guard x == 0 before clz/ctz.
- C++20 <bit> header: std::popcount, std::countr_zero, std::countl_zero, std::bit_width, std::bit_floor, std::bit_ceil, std::rotl, std::rotr.
- For 1<<i, use 1u<<i or 1ULL<<i when i may be large.

### Python
- x.bit_count(), x.bit_length()
- ctz: (x & -x).bit_length() - 1 (x > 0)
- Leading zeros for fixed width w: w - x.bit_length()
- Python ints are arbitrary precision; still use word-wise loops for performance and avoid Python-level per-bit loops when n is large.

### Java
- Integer.bitCount(x), Long.bitCount(x)
- Integer.numberOfTrailingZeros(x), Long.numberOfTrailingZeros(x)
- Integer.highestOneBit(x), Long.highestOneBit(x)
- Integer.lowestOneBit(x), Long.lowestOneBit(x)
- Integer.rotateLeft/rotateRight
- Use unsigned ops carefully with Java 8+ (Integer.divideUnsigned, etc.)

### Rust
- Methods on unsigned primitives u32/u64/etc: count_ones, trailing_zeros, leading_zeros, rotate_left, is_power_of_two, next_power_of_two, ilog2/ilog10 (stable), saturating_* variants
- Prefer u64 for masks; use 1u64 << i.

## 10) Common pitfalls

- C/C++ shifting negatives or overflowing signed left-shifts is undefined behavior. Use unsigned types for bit hacks.
- Guard x == 0 when using __builtin_clz/__builtin_ctz.
- Ensure literal width: 1<<i may overflow 32-bit; use 1u or 1ULL.
- Parentheses with bitwise vs comparison: (a & b) == 0 not a & b == 0 ambiguously read; write it clearly.
- Python: avoid per-bit Python loops for large widths; rely on integer ops and vectorized patterns.
- SOS DP and 2^n arrays: memory is O(n·2^n); check constraints and type sizes.

## 11) Ready-to-use templates

### 11.1 Basic helpers

C++:

inline bool is_pow2(unsigned long long x){ return x && !(x & (x-1)); }
inline unsigned long long lowbit(unsigned long long x){ return x & -x; }
inline int ctzll(unsigned long long x){ return __builtin_ctzll(x); } // x != 0
inline int popcnt(unsigned long long x){ return __builtin_popcountll(x); }
inline unsigned long long msb(unsigned long long x){ return x ? 1ULL << (63 - __builtin_clzll(x)) : 0ULL; }
inline unsigned long long bit_ceil_ull(unsigned long long x){
  if (x <= 1) return x ? 1ULL : 0ULL;
  x--; x |= x>>1; x |= x>>2; x |= x>>4; x |= x>>8; x |= x>>16; x |= x>>32; return x+1;
}

Python:

def is_pow2(x: int) -> bool: return x > 0 and (x & (x-1)) == 0

def lowbit(x: int) -> int: return x & -x

def ctz(x: int) -> int: return (x & -x).bit_length() - 1 if x > 0 else -1

def msb(x: int) -> int: return (1 << (x.bit_length() - 1)) if x > 0 else 0

def bit_ceil(x: int) -> int:
    if x <= 1: return x if x >= 0 else 0
    y = x - 1
    y |= y >> 1; y |= y >> 2; y |= y >> 4; y |= y >> 8; y |= y >> 16
    # extend if needed for big ints
    shift = 32
    while (1 << shift) <= y:
        y |= y >> shift
        shift <<= 1
    return y + 1

### 11.2 Submask iteration

C++:

for (int sub = m; ; sub = (sub - 1) & m) {
  // use sub
  if (sub == 0) break;
}

Python:

sub = m
while True:
    # use sub
    if sub == 0: break
    sub = (sub - 1) & m

### 11.3 Iterate set bits with indices

C++:

for (int s = m; s; s &= s - 1) {
  int i = __builtin_ctz(s);
  // use i
}

Python:

s = m
while s:
    lsb = s & -s
    i = lsb.bit_length() - 1
    s ^= lsb

### 11.4 SOS DP (zeta transform)

C++:

for (int i = 0; i < n; ++i)
  for (int mask = 0; mask < (1<<n); ++mask)
    if (mask & (1<<i)) F[mask] += F[mask ^ (1<<i)];

Python:

for i in range(n):
    for mask in range(1<<n):
        if mask >> i & 1:
            F[mask] += F[mask ^ (1<<i)]

### 11.5 XOR basis

C++: see §7.3 struct XorBasis. Python: class XorBasis above.

### 11.6 Gosper’s hack

C++: see §5 next_comb. Python: see §5 next_comb.

## 12) Problem patterns checklist

- DP on subsets (TSP, assignment, set cover, Steiner tree on small k)
- Submask convolution / partition DP
- SOS DP for subset aggregations (counts, sums, OR/AND/XOR transforms)
- XOR basis for max XOR, counting distinct XORs, checking representability
- Meet-in-the-middle with bitsets/integers for set operations
- Graph bitset optimizations: triangle counting, transitive closure, reachability layers
- Sliding masks for fixed-length windows or bit DP constraints

## 13) Quick complexity reference

- All masks: O(2^n)
- For fixed mask m, all submasks: O(2^{|m|})
- All submasks of all masks: O(3^n)
- SOS DP: O(n·2^n)
- TSP DP: O(n^2·2^n)
- XOR basis build: O(LOG·N)

## 14) Final tips

- Prefer unsigned integers for bit tricks in C/C++.
- Guard zero inputs for clz/ctz.
- Precompute and reuse popcounts; often faster than recomputing.
- For Python, favor large integer ops over Python loops; PyPy can help.
- Keep templates ready; copy-paste and adapt under contest time.