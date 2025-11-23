# Graph Theory & Algorithms: Complete Guide - Part 2 (Advanced)

## Table of Contents
1. [Topological Sort](#topological-sort)
2. [Shortest Path Algorithms](#shortest-path-algorithms)
3. [Minimum Spanning Tree](#minimum-spanning-tree)
4. [Union-Find (Disjoint Set)](#union-find-disjoint-set)
5. [Advanced Graph Problems](#advanced-graph-problems)
6. [Graph Problem-Solving Strategy](#graph-problem-solving-strategy)

---

## Topological Sort

### 🧠 Concept
**Topological Sort**: Linear ordering of vertices in a DAG such that for every directed edge u → v, u comes before v in the ordering.

**Use Cases**:
- Task scheduling with dependencies
- Course prerequisites
- Build systems
- Package managers

### Requirements
- Graph must be a **DAG** (Directed Acyclic Graph)
- If graph has a cycle, topological sort is impossible

### Example
```
Graph (Prerequisites):
    0 → 1 → 3
    ↓   ↓
    2 → 4

Valid topological orders:
- [0, 1, 2, 3, 4]
- [0, 2, 1, 3, 4]
- [0, 1, 2, 4, 3]
- [0, 2, 1, 4, 3]

All ensure: if A → B, then A comes before B
```

### Method 1: DFS-Based (Post-order)

```python
def topological_sort_dfs(graph, n):
    """
    Topological sort using DFS
    
    Algorithm:
    1. Do DFS from each unvisited node
    2. After exploring all neighbors, add node to result
    3. Reverse the result
    
    Time: O(V + E)
    Space: O(V)
    """
    visited = set()
    result = []
    
    def dfs(node):
        visited.add(node)
        
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                dfs(neighbor)
        
        # Add to result AFTER exploring all neighbors
        result.append(node)
    
    # Process all nodes
    for i in range(n):
        if i not in visited:
            dfs(i)
    
    # Reverse to get topological order
    return result[::-1]

# Example
graph = {
    0: [1, 2],
    1: [3],
    2: [3],
    3: []
}
print(topological_sort_dfs(graph, 4))  # [0, 2, 1, 3] or [0, 1, 2, 3]
```

### Method 2: Kahn's Algorithm (BFS-Based)

```python
from collections import deque

def topological_sort_kahn(graph, n):
    """
    Topological sort using Kahn's algorithm (BFS)
    
    Algorithm:
    1. Calculate in-degree for each node
    2. Start with nodes that have in-degree 0
    3. Process them and reduce in-degree of neighbors
    4. Add nodes with in-degree 0 to queue
    
    Bonus: Can detect cycles (if result length < n)
    
    Time: O(V + E)
    Space: O(V)
    """
    # Calculate in-degrees
    in_degree = [0] * n
    for node in graph:
        for neighbor in graph[node]:
            in_degree[neighbor] += 1
    
    # Start with nodes having in-degree 0
    queue = deque([i for i in range(n) if in_degree[i] == 0])
    result = []
    
    while queue:
        node = queue.popleft()
        result.append(node)
        
        # Reduce in-degree of neighbors
        for neighbor in graph.get(node, []):
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
    
    # If result doesn't have all nodes, there's a cycle
    if len(result) != n:
        return []  # Cycle detected
    
    return result

# Example
print(topological_sort_kahn(graph, 4))  # [0, 1, 2, 3] or similar
```

### Application: Course Schedule

```python
def canFinish(numCourses, prerequisites):
    """
    LeetCode 207: Course Schedule
    
    Determine if you can finish all courses given prerequisites
    prerequisites[i] = [ai, bi] means to take ai you must take bi first
    
    This is cycle detection in directed graph!
    """
    # Build adjacency list
    graph = {i: [] for i in range(numCourses)}
    for course, prereq in prerequisites:
        graph[prereq].append(course)
    
    # Try topological sort
    result = topological_sort_kahn(graph, numCourses)
    return len(result) == numCourses

# Test
print(canFinish(2, [[1, 0]]))  # True
print(canFinish(2, [[1, 0], [0, 1]]))  # False (cycle)

def findOrder(numCourses, prerequisites):
    """
    LeetCode 210: Course Schedule II
    
    Return the order to take courses, or [] if impossible
    """
    graph = {i: [] for i in range(numCourses)}
    for course, prereq in prerequisites:
        graph[prereq].append(course)
    
    return topological_sort_kahn(graph, numCourses)

# Test
print(findOrder(4, [[1, 0], [2, 0], [3, 1], [3, 2]]))
# [0, 1, 2, 3] or [0, 2, 1, 3]
```

---

## Shortest Path Algorithms

### Algorithm 1: Dijkstra's Algorithm

**Use**: Find shortest path from source to all vertices in **weighted graph with non-negative weights**

**Cannot handle**: Negative edge weights

```python
import heapq

def dijkstra(graph, start, n):
    """
    Dijkstra's shortest path algorithm
    
    Args:
        graph: adjacency list with (neighbor, weight)
        start: starting vertex
        n: number of vertices
    
    Returns:
        distances: array where distances[i] = shortest distance from start to i
    
    Time: O((V + E) log V) with binary heap
    Space: O(V)
    """
    # Initialize distances to infinity
    distances = [float('inf')] * n
    distances[start] = 0
    
    # Min heap: (distance, node)
    heap = [(0, start)]
    
    while heap:
        current_dist, node = heapq.heappop(heap)
        
        # Skip if we've already found a better path
        if current_dist > distances[node]:
            continue
        
        # Explore neighbors
        for neighbor, weight in graph.get(node, []):
            distance = current_dist + weight
            
            # If found shorter path
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                heapq.heappush(heap, (distance, neighbor))
    
    return distances

# Example
graph = {
    0: [(1, 4), (2, 1)],
    1: [(3, 1)],
    2: [(1, 2), (3, 5)],
    3: []
}
print(dijkstra(graph, 0, 4))  # [0, 3, 1, 4]
# Shortest paths: 0->0=0, 0->2->1=3, 0->2=1, 0->2->1->3=4
```

### Dijkstra with Path Reconstruction

```python
def dijkstra_with_path(graph, start, end, n):
    """
    Dijkstra that returns both distance and actual path
    """
    distances = [float('inf')] * n
    distances[start] = 0
    parent = [-1] * n
    
    heap = [(0, start)]
    
    while heap:
        current_dist, node = heapq.heappop(heap)
        
        if node == end:
            break
        
        if current_dist > distances[node]:
            continue
        
        for neighbor, weight in graph.get(node, []):
            distance = current_dist + weight
            
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                parent[neighbor] = node
                heapq.heappush(heap, (distance, neighbor))
    
    # Reconstruct path
    path = []
    current = end
    while current != -1:
        path.append(current)
        current = parent[current]
    path.reverse()
    
    return distances[end], path

# Example
dist, path = dijkstra_with_path(graph, 0, 3, 4)
print(f"Distance: {dist}, Path: {path}")  # Distance: 4, Path: [0, 2, 1, 3]
```

### Application: Network Delay Time

```python
def networkDelayTime(times, n, k):
    """
    LeetCode 743: Network Delay Time
    
    times[i] = [ui, vi, wi] means signal travels from ui to vi in wi time
    Return minimum time for all nodes to receive signal from k
    """
    # Build graph
    graph = {i: [] for i in range(1, n + 1)}
    for u, v, w in times:
        graph[u].append((v, w))
    
    # Run Dijkstra from k
    distances = dijkstra(graph, k, n + 1)
    
    # Get max distance (excluding index 0 and infinity)
    max_dist = max(distances[1:])
    return max_dist if max_dist != float('inf') else -1
```

---

### Algorithm 2: Bellman-Ford

**Use**: Shortest path with **negative edge weights** allowed

**Can detect**: Negative cycles

```python
def bellman_ford(edges, n, start):
    """
    Bellman-Ford algorithm
    
    Args:
        edges: list of (u, v, weight)
        n: number of vertices (0 to n-1)
        start: starting vertex
    
    Returns:
        distances: shortest distances from start
        or None if negative cycle detected
    
    Time: O(V * E)
    Space: O(V)
    """
    distances = [float('inf')] * n
    distances[start] = 0
    
    # Relax edges (n-1) times
    for _ in range(n - 1):
        for u, v, weight in edges:
            if distances[u] != float('inf') and distances[u] + weight < distances[v]:
                distances[v] = distances[u] + weight
    
    # Check for negative cycles
    for u, v, weight in edges:
        if distances[u] != float('inf') and distances[u] + weight < distances[v]:
            return None  # Negative cycle detected
    
    return distances

# Example
edges = [(0, 1, 4), (0, 2, 1), (2, 1, 2), (1, 3, 1), (2, 3, 5)]
print(bellman_ford(edges, 4, 0))  # [0, 3, 1, 4]

# With negative edge
edges_neg = [(0, 1, 1), (1, 2, -3), (2, 3, 3), (3, 1, -2)]
print(bellman_ford(edges_neg, 4, 0))  # None (negative cycle)
```

---

### Algorithm 3: Floyd-Warshall

**Use**: All-pairs shortest paths

**Pros**: Simple, works with negative edges
**Cons**: O(V³) time complexity

```python
def floyd_warshall(graph_matrix):
    """
    Floyd-Warshall: Find shortest paths between ALL pairs
    
    Args:
        graph_matrix[i][j]: weight of edge from i to j
                           (use inf if no edge)
    
    Returns:
        Distance matrix with shortest paths
    
    Time: O(V^3)
    Space: O(V^2)
    """
    n = len(graph_matrix)
    dist = [row[:] for row in graph_matrix]  # Copy matrix
    
    # Try all intermediate vertices
    for k in range(n):
        for i in range(n):
            for j in range(n):
                # Is path i -> k -> j shorter than current i -> j?
                dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])
    
    return dist

# Example
INF = float('inf')
graph = [
    [0,   3, INF,   7],
    [8,   0,   2, INF],
    [5, INF,   0,   1],
    [2, INF, INF,   0]
]

distances = floyd_warshall(graph)
for row in distances:
    print(row)
# All-pairs shortest distances
```

---

## Minimum Spanning Tree

**Definition**: Subset of edges that connects all vertices with minimum total weight (no cycles)

**Applications**: Network design, clustering, approximation algorithms

### Algorithm 1: Kruskal's Algorithm

**Approach**: Greedy - Pick smallest edge that doesn't create cycle

**Uses**: Union-Find data structure

```python
class UnionFind:
    """Union-Find (Disjoint Set) data structure"""
    
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n
    
    def find(self, x):
        """Find root with path compression"""
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]
    
    def union(self, x, y):
        """Union by rank"""
        root_x = self.find(x)
        root_y = self.find(y)
        
        if root_x == root_y:
            return False
        
        if self.rank[root_x] < self.rank[root_y]:
            self.parent[root_x] = root_y
        elif self.rank[root_x] > self.rank[root_y]:
            self.parent[root_y] = root_x
        else:
            self.parent[root_y] = root_x
            self.rank[root_x] += 1
        
        return True

def kruskal_mst(n, edges):
    """
    Kruskal's MST algorithm
    
    Args:
        n: number of vertices
        edges: list of (u, v, weight)
    
    Returns:
        (total_weight, mst_edges)
    
    Time: O(E log E) for sorting
    Space: O(V)
    """
    # Sort edges by weight
    edges.sort(key=lambda x: x[2])
    
    uf = UnionFind(n)
    mst_edges = []
    total_weight = 0
    
    for u, v, weight in edges:
        # If adding this edge doesn't create cycle
        if uf.union(u, v):
            mst_edges.append((u, v, weight))
            total_weight += weight
            
            # MST has n-1 edges
            if len(mst_edges) == n - 1:
                break
    
    return total_weight, mst_edges

# Example
edges = [
    (0, 1, 4), (0, 2, 1), (1, 2, 2),
    (1, 3, 5), (2, 3, 8), (2, 4, 10),
    (3, 4, 2), (3, 5, 6), (4, 5, 3)
]
weight, mst = kruskal_mst(6, edges)
print(f"MST Weight: {weight}")  # 14
print(f"MST Edges: {mst}")
```

---

### Algorithm 2: Prim's Algorithm

**Approach**: Greedy - Grow MST from a starting vertex

```python
def prim_mst(graph, n):
    """
    Prim's MST algorithm
    
    Args:
        graph: adjacency list with (neighbor, weight)
        n: number of vertices
    
    Returns:
        Total MST weight
    
    Time: O(E log V) with heap
    Space: O(V)
    """
    visited = set([0])
    edges = [(weight, 0, neighbor) for neighbor, weight in graph[0]]
    heapq.heapify(edges)
    
    mst_weight = 0
    mst_edges = []
    
    while edges and len(visited) < n:
        weight, frm, to = heapq.heappop(edges)
        
        if to in visited:
            continue
        
        visited.add(to)
        mst_weight += weight
        mst_edges.append((frm, to, weight))
        
        for neighbor, w in graph.get(to, []):
            if neighbor not in visited:
                heapq.heappush(edges, (w, to, neighbor))
    
    return mst_weight, mst_edges

# Example (same graph as Kruskal)
graph = {
    0: [(1, 4), (2, 1)],
    1: [(0, 4), (2, 2), (3, 5)],
    2: [(0, 1), (1, 2), (3, 8), (4, 10)],
    3: [(1, 5), (2, 8), (4, 2), (5, 6)],
    4: [(2, 10), (3, 2), (5, 3)],
    5: [(3, 6), (4, 3)]
}
weight, mst = prim_mst(graph, 6)
print(f"MST Weight: {weight}")  # 14
```

---

## Union-Find (Disjoint Set)

**Use Cases**:
- Kruskal's MST
- Detecting cycles
- Connected components
- Network connectivity

### Implementation with Optimizations

```python
class UnionFind:
    """
    Union-Find with path compression and union by rank
    
    Operations: O(α(n)) ≈ O(1) amortized
    where α is inverse Ackermann function
    """
    
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n
        self.components = n
    
    def find(self, x):
        """Find with path compression"""
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])  # Path compression
        return self.parent[x]
    
    def union(self, x, y):
        """Union by rank"""
        root_x = self.find(x)
        root_y = self.find(y)
        
        if root_x == root_y:
            return False  # Already connected
        
        # Union by rank
        if self.rank[root_x] < self.rank[root_y]:
            self.parent[root_x] = root_y
        elif self.rank[root_x] > self.rank[root_y]:
            self.parent[root_y] = root_x
        else:
            self.parent[root_y] = root_x
            self.rank[root_x] += 1
        
        self.components -= 1
        return True
    
    def connected(self, x, y):
        """Check if x and y are in same component"""
        return self.find(x) == self.find(y)
    
    def count_components(self):
        """Return number of disjoint components"""
        return self.components

# Example usage
uf = UnionFind(5)
uf.union(0, 1)
uf.union(2, 3)
print(uf.connected(0, 1))  # True
print(uf.connected(0, 2))  # False
print(uf.count_components())  # 3
```

### Application: Number of Connected Components

```python
def countComponents(n, edges):
    """
    LeetCode 323: Number of Connected Components
    
    Given n nodes and list of undirected edges,
    count number of connected components
    """
    uf = UnionFind(n)
    
    for u, v in edges:
        uf.union(u, v)
    
    return uf.count_components()

# Test
print(countComponents(5, [[0, 1], [1, 2], [3, 4]]))  # 2
```

### Application: Redundant Connection

```python
def findRedundantConnection(edges):
    """
    LeetCode 684: Redundant Connection
    
    Find edge that, when removed, makes tree
    (the last edge that creates a cycle)
    """
    n = len(edges)
    uf = UnionFind(n + 1)
    
    for u, v in edges:
        if not uf.union(u, v):
            return [u, v]  # This edge creates cycle
    
    return []

# Test
print(findRedundantConnection([[1, 2], [1, 3], [2, 3]]))  # [2, 3]
```

---

## Advanced Graph Problems

### Problem 1: Bipartite Graph Check

**Bipartite**: Can color graph with 2 colors such that no adjacent nodes have same color

**Applications**: Matching problems, scheduling

```python
from collections import deque

def isBipartite(graph):
    """
    Check if graph is bipartite using BFS coloring
    
    Time: O(V + E)
    Space: O(V)
    """
    n = len(graph)
    color = [-1] * n  # -1 = uncolored, 0/1 = colors
    
    for start in range(n):
        if color[start] != -1:
            continue
        
        # BFS coloring
        queue = deque([start])
        color[start] = 0
        
        while queue:
            node = queue.popleft()
            
            for neighbor in graph[node]:
                if color[neighbor] == -1:
                    # Color with opposite color
                    color[neighbor] = 1 - color[node]
                    queue.append(neighbor)
                elif color[neighbor] == color[node]:
                    # Same color = not bipartite
                    return False
    
    return True

# Test
graph = [[1, 3], [0, 2], [1, 3], [0, 2]]
print(isBipartite(graph))  # True (can color with 2 colors)

graph = [[1, 2, 3], [0, 2], [0, 1, 3], [0, 2]]
print(isBipartite(graph))  # False
```

---

### Problem 2: Shortest Bridge

**Problem**: Find smallest number of flips to connect two islands

```python
def shortestBridge(grid):
    """
    LeetCode 934: Shortest Bridge
    
    Strategy:
    1. Find first island using DFS
    2. Use BFS from first island to find second island
    """
    n = len(grid)
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    
    def dfs(r, c, island):
        """Mark all cells of first island"""
        if r < 0 or r >= n or c < 0 or c >= n or grid[r][c] != 1:
            return
        
        grid[r][c] = 2  # Mark as visited
        island.append((r, c))
        
        for dr, dc in directions:
            dfs(r + dr, c + dc, island)
    
    # Find first island
    first_island = []
    found = False
    for r in range(n):
        for c in range(n):
            if grid[r][c] == 1:
                dfs(r, c, first_island)
                found = True
                break
        if found:
            break
    
    # BFS from first island to find second island
    queue = deque([(r, c, 0) for r, c in first_island])
    
    while queue:
        r, c, dist = queue.popleft()
        
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            
            if 0 <= nr < n and 0 <= nc < n:
                if grid[nr][nc] == 1:
                    return dist  # Found second island
                elif grid[nr][nc] == 0:
                    grid[nr][nc] = 2  # Mark as visited
                    queue.append((nr, nc, dist + 1))
    
    return -1
```

---

### Problem 3: Critical Connections (Bridges)

**Bridge**: Edge whose removal disconnects the graph

```python
def criticalConnections(n, connections):
    """
    LeetCode 1192: Critical Connections
    
    Find all bridges using Tarjan's algorithm
    
    Time: O(V + E)
    """
    graph = {i: [] for i in range(n)}
    for u, v in connections:
        graph[u].append(v)
        graph[v].append(u)
    
    visited = [False] * n
    disc = [0] * n  # Discovery time
    low = [0] * n   # Lowest reachable vertex
    parent = [-1] * n
    bridges = []
    time = [0]
    
    def dfs(u):
        visited[u] = True
        disc[u] = low[u] = time[0]
        time[0] += 1
        
        for v in graph[u]:
            if not visited[v]:
                parent[v] = u
                dfs(v)
                
                # Update low value
                low[u] = min(low[u], low[v])
                
                # If lowest reachable from v is higher than u's discovery time
                # Then (u, v) is a bridge
                if low[v] > disc[u]:
                    bridges.append([u, v])
            
            elif v != parent[u]:  # Back edge
                low[u] = min(low[u], disc[v])
    
    for i in range(n):
        if not visited[i]:
            dfs(i)
    
    return bridges

# Test
connections = [[0, 1], [1, 2], [2, 0], [1, 3]]
print(criticalConnections(4, connections))  # [[1, 3]]
```

---

### Problem 4: Word Ladder

**Problem**: Transform one word to another, changing one letter at a time

```python
from collections import deque, defaultdict

def ladderLength(beginWord, endWord, wordList):
    """
    LeetCode 127: Word Ladder
    
    Find shortest transformation sequence
    
    Strategy: Build graph where words are nodes,
    edges connect words differing by 1 letter
    Then BFS for shortest path
    
    Time: O(M^2 * N) where M = word length, N = word list size
    """
    if endWord not in wordList:
        return 0
    
    wordList.append(beginWord)
    
    # Build adjacency list using patterns
    # e.g., "hot" -> "*ot", "h*t", "ho*"
    patterns = defaultdict(list)
    for word in wordList:
        for i in range(len(word)):
            pattern = word[:i] + '*' + word[i+1:]
            patterns[pattern].append(word)
    
    # BFS
    queue = deque([(beginWord, 1)])
    visited = {beginWord}
    
    while queue:
        word, level = queue.popleft()
        
        if word == endWord:
            return level
        
        # Try all patterns
        for i in range(len(word)):
            pattern = word[:i] + '*' + word[i+1:]
            
            for neighbor in patterns[pattern]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, level + 1))
    
    return 0

# Test
print(ladderLength("hit", "cog", ["hot", "dot", "dog", "lot", "log", "cog"]))
# 5: "hit" -> "hot" -> "dot" -> "dog" -> "cog"
```

---

## Graph Problem-Solving Strategy

### Step 1: Identify Graph Type
- **Directed** or **Undirected**?
- **Weighted** or **Unweighted**?
- **Cyclic** or **Acyclic**?
- Tree (special graph)?

### Step 2: Choose Representation
- Small/dense graph → Adjacency matrix
- Large/sparse graph → Adjacency list
- Simple edges → Edge list

### Step 3: Recognize Pattern

| Problem Type | Algorithm |
|-------------|-----------|
| Shortest path (unweighted) | BFS |
| Shortest path (weighted, non-negative) | Dijkstra |
| Shortest path (negative weights) | Bellman-Ford |
| All-pairs shortest path | Floyd-Warshall |
| Minimum spanning tree | Kruskal or Prim |
| Detect cycle | DFS (directed), Union-Find (undirected) |
| Topological sort | DFS or Kahn's |
| Connected components | DFS or Union-Find |
| Bipartite check | BFS coloring |
| Find bridges/articulation points | Tarjan's |

### Step 4: Template Application

1. **BFS Template**: Shortest path, level-order
2. **DFS Template**: Exploration, backtracking, cycle detection
3. **Dijkstra Template**: Weighted shortest path
4. **Union-Find Template**: Connectivity, MST

---

## Summary & Tips

### Key Takeaways

1. **BFS vs DFS**:
   - BFS: Shortest path, level by level
   - DFS: Exploration, backtracking

2. **Shortest Path Algorithms**:
   - Unweighted → BFS
   - Weighted (non-negative) → Dijkstra
   - Negative weights → Bellman-Ford
   - All pairs → Floyd-Warshall

3. **MST Algorithms**:
   - Kruskal: Sort edges, use Union-Find
   - Prim: Grow from start, use heap

4. **Common Patterns**:
   - Grid problems → DFS/BFS with directions
   - Prerequisites → Topological sort
   - Connectivity → Union-Find
   - Islands → DFS/BFS on 2D grid

### Practice Strategy

1. Master BFS and DFS first
2. Learn one shortest path algorithm (Dijkstra)
3. Understand Union-Find
4. Practice topological sort problems
5. Move to advanced algorithms

### Recommended Problem Sequence

**Beginner**:
1. Number of Islands
2. Clone Graph
3. Course Schedule
4. Pacific Atlantic Water Flow

**Intermediate**:
5. Network Delay Time
6. Cheapest Flights Within K Stops
7. Word Ladder
8. Evaluate Division

**Advanced**:
9. Critical Connections
10. Shortest Bridge
11. Minimum Cost to Connect All Points
12. Swim in Rising Water

---

**Remember**: Graph problems often combine multiple concepts. Break them down step by step!
