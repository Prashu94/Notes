# Graph Theory & Algorithms: Complete Guide - Part 1 (Fundamentals)

## Table of Contents
1. [What are Graphs?](#what-are-graphs)
2. [Graph Terminology](#graph-terminology)
3. [Graph Representations](#graph-representations)
4. [Core Graph Traversal Algorithms](#core-graph-traversal-algorithms)
5. [BFS (Breadth-First Search)](#bfs-breadth-first-search)
6. [DFS (Depth-First Search)](#dfs-depth-first-search)
7. [Common Graph Patterns](#common-graph-patterns)

---

## What are Graphs?

**A graph** is a data structure consisting of:
- **Vertices (Nodes)**: Points/entities
- **Edges**: Connections between vertices

### Real-World Examples
- **Social Networks**: People (vertices), Friendships (edges)
- **Maps**: Cities (vertices), Roads (edges)
- **Web Pages**: Pages (vertices), Hyperlinks (edges)
- **Dependencies**: Tasks (vertices), Dependencies (edges)

### Visual Example
```
Simple Graph:
    A --- B
    |     |
    C --- D

Vertices: {A, B, C, D}
Edges: {(A,B), (A,C), (B,D), (C,D)}
```

---

## Graph Terminology

### 1. **Directed vs Undirected Graphs**

**Undirected Graph**: Edges have no direction (bidirectional)
```
A --- B  (A can reach B, B can reach A)
```

**Directed Graph (Digraph)**: Edges have direction
```
A --> B  (A can reach B, but B cannot reach A)
```

### 2. **Weighted vs Unweighted Graphs**

**Unweighted**: All edges have equal cost
```
A --- B
```

**Weighted**: Edges have different costs/weights
```
    5
A ----- B
    2
C ----- D
```

### 3. **Connected vs Disconnected**

**Connected**: Path exists between every pair of vertices
```
A --- B --- C  (All connected)
```

**Disconnected**: Some vertices are isolated
```
A --- B    C --- D  (Two separate components)
```

### 4. **Cyclic vs Acyclic**

**Cyclic**: Contains at least one cycle (path that starts and ends at same vertex)
```
A --> B
^     |
|     v
D <-- C  (Cycle: A->B->C->D->A)
```

**Acyclic**: No cycles
```
A --> B --> C  (No way to return to A)
```

**DAG (Directed Acyclic Graph)**: Directed graph with no cycles
- Used in: Task scheduling, dependency resolution

### 5. **Degree**

**In-degree**: Number of incoming edges
**Out-degree**: Number of outgoing edges
**Degree**: Total edges connected to a vertex (undirected graph)

```
    A --> B --> C
    |           ^
    v           |
    D ----------+

A: in=0, out=2
B: in=1, out=1
C: in=2, out=0
D: in=1, out=1
```

### 6. **Path vs Cycle**

**Path**: Sequence of vertices connected by edges
**Simple Path**: No repeated vertices
**Cycle**: Path that starts and ends at the same vertex

---

## Graph Representations

### Representation 1: Adjacency Matrix

**Definition**: 2D array where `matrix[i][j] = 1` means edge from i to j

```python
# Example: Graph with 4 vertices
#     0 --- 1
#     |     |
#     2 --- 3

# Adjacency Matrix (Undirected)
graph = [
    [0, 1, 1, 0],  # 0 connects to 1, 2
    [1, 0, 0, 1],  # 1 connects to 0, 3
    [1, 0, 0, 1],  # 2 connects to 0, 3
    [0, 1, 1, 0]   # 3 connects to 1, 2
]

# For weighted graph
graph_weighted = [
    [0,   5,   2,   0],
    [5,   0,   0,   3],
    [2,   0,   0,   4],
    [0,   3,   4,   0]
]
```

**Pros**:
- O(1) edge lookup: `graph[i][j]`
- Simple to implement
- Good for dense graphs

**Cons**:
- O(V²) space (V = number of vertices)
- Inefficient for sparse graphs
- Iterating neighbors: O(V)

---

### Representation 2: Adjacency List (Most Common)

**Definition**: Array of lists where `graph[i]` contains all neighbors of vertex i

```python
# Same graph using adjacency list
graph = {
    0: [1, 2],
    1: [0, 3],
    2: [0, 3],
    3: [1, 2]
}

# For weighted graph: store (neighbor, weight) tuples
graph_weighted = {
    0: [(1, 5), (2, 2)],
    1: [(0, 5), (3, 3)],
    2: [(0, 2), (3, 4)],
    3: [(1, 3), (2, 4)]
}

# Using defaultdict for cleaner code
from collections import defaultdict

graph = defaultdict(list)
graph[0].append(1)
graph[0].append(2)
graph[1].append(0)
# ... etc
```

**Pros**:
- O(V + E) space (E = number of edges)
- Efficient for sparse graphs
- Fast neighbor iteration: O(degree)

**Cons**:
- Edge lookup: O(degree)
- Slightly more complex

---

### Representation 3: Edge List

**Definition**: List of all edges

```python
# Unweighted
edges = [(0, 1), (0, 2), (1, 3), (2, 3)]

# Weighted
edges = [(0, 1, 5), (0, 2, 2), (1, 3, 3), (2, 3, 4)]
```

**Use Cases**: Kruskal's MST algorithm, simple graph input

---

### Building a Graph from Input

```python
def build_graph_from_edges(n, edges, directed=False):
    """
    Build adjacency list from edge list
    
    Args:
        n: number of vertices (0 to n-1)
        edges: list of (u, v) or (u, v, weight)
        directed: whether graph is directed
    """
    from collections import defaultdict
    
    graph = defaultdict(list)
    
    for edge in edges:
        if len(edge) == 2:
            u, v = edge
            weight = 1
        else:
            u, v, weight = edge
        
        graph[u].append((v, weight))
        if not directed:
            graph[v].append((u, weight))
    
    return graph

# Example usage
edges = [(0, 1), (0, 2), (1, 3), (2, 3)]
graph = build_graph_from_edges(4, edges)
print(graph)
# {0: [(1, 1), (2, 1)], 1: [(0, 1), (3, 1)], 2: [(0, 1), (3, 1)], 3: [(1, 1), (2, 1)]}
```

---

## Core Graph Traversal Algorithms

**Traversal** = Visiting all vertices in a graph

Two fundamental approaches:
1. **BFS (Breadth-First Search)**: Explore level by level
2. **DFS (Depth-First Search)**: Explore as deep as possible first

---

## BFS (Breadth-First Search)

### 🧠 Concept
- Explore neighbors first before going deeper
- Uses a **Queue** (FIFO)
- Explores in "layers" or "levels"

### Visual Example
```
Graph:
    0
   / \
  1   2
  |   |
  3   4

BFS starting from 0:
Level 0: [0]
Level 1: [1, 2]
Level 2: [3, 4]

Order visited: 0 → 1 → 2 → 3 → 4
```

### Template Code

```python
from collections import deque

def bfs(graph, start):
    """
    BFS traversal returning list of visited nodes
    
    Time: O(V + E)
    Space: O(V)
    """
    visited = set()
    queue = deque([start])
    visited.add(start)
    result = []
    
    while queue:
        node = queue.popleft()
        result.append(node)
        
        # Explore neighbors
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    
    return result

# Example
graph = {
    0: [1, 2],
    1: [0, 3],
    2: [0, 4],
    3: [1],
    4: [2]
}

print(bfs(graph, 0))  # [0, 1, 2, 3, 4]
```

### BFS with Levels (Track Distance)

```python
def bfs_levels(graph, start):
    """
    BFS that tracks the level/distance of each node
    
    Returns: dict mapping node -> distance from start
    """
    visited = set([start])
    queue = deque([(start, 0)])  # (node, level)
    levels = {start: 0}
    
    while queue:
        node, level = queue.popleft()
        
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                levels[neighbor] = level + 1
                queue.append((neighbor, level + 1))
    
    return levels

# Example
levels = bfs_levels(graph, 0)
print(levels)  # {0: 0, 1: 1, 2: 1, 3: 2, 4: 2}
```

### When to Use BFS

✅ **Use BFS when**:
1. Finding **shortest path** in unweighted graph
2. Finding **minimum number of steps**
3. **Level-order traversal**
4. Finding **connected components**
5. Checking if graph is **bipartite**

### BFS Applications

#### Application 1: Shortest Path in Unweighted Graph

```python
def shortest_path_bfs(graph, start, end):
    """
    Find shortest path from start to end
    
    Returns: path as list, or None if no path exists
    """
    if start == end:
        return [start]
    
    visited = set([start])
    queue = deque([(start, [start])])  # (node, path_to_node)
    
    while queue:
        node, path = queue.popleft()
        
        for neighbor in graph[node]:
            if neighbor == end:
                return path + [neighbor]
            
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
    
    return None  # No path exists

# Example
path = shortest_path_bfs(graph, 0, 4)
print(path)  # [0, 2, 4]
```

#### Application 2: Level-Order Traversal (Tree)

```python
def level_order_traversal(root):
    """
    Print nodes level by level (for trees)
    
    Returns: list of lists, each inner list is one level
    """
    if not root:
        return []
    
    result = []
    queue = deque([root])
    
    while queue:
        level_size = len(queue)
        current_level = []
        
        for _ in range(level_size):
            node = queue.popleft()
            current_level.append(node.val)
            
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        
        result.append(current_level)
    
    return result
```

---

## DFS (Depth-First Search)

### 🧠 Concept
- Explore as deep as possible before backtracking
- Uses **Stack** (or recursion which uses call stack)
- Explores one branch completely before trying another

### Visual Example
```
Graph:
    0
   / \
  1   2
  |   |
  3   4

DFS starting from 0 (going left first):
0 → 1 → 3 (dead end, backtrack) → 2 → 4

Order visited: 0 → 1 → 3 → 2 → 4
```

### Template Code: Recursive

```python
def dfs_recursive(graph, node, visited=None):
    """
    DFS traversal using recursion
    
    Time: O(V + E)
    Space: O(V) for recursion stack
    """
    if visited is None:
        visited = set()
    
    visited.add(node)
    result = [node]
    
    for neighbor in graph[node]:
        if neighbor not in visited:
            result.extend(dfs_recursive(graph, neighbor, visited))
    
    return result

# Example
print(dfs_recursive(graph, 0))  # [0, 1, 3, 2, 4]
```

### Template Code: Iterative (with Stack)

```python
def dfs_iterative(graph, start):
    """
    DFS traversal using explicit stack
    
    Time: O(V + E)
    Space: O(V)
    """
    visited = set()
    stack = [start]
    result = []
    
    while stack:
        node = stack.pop()
        
        if node not in visited:
            visited.add(node)
            result.append(node)
            
            # Add neighbors to stack (reverse order for left-first)
            for neighbor in reversed(graph[node]):
                if neighbor not in visited:
                    stack.append(neighbor)
    
    return result

# Example
print(dfs_iterative(graph, 0))  # [0, 1, 3, 2, 4]
```

### When to Use DFS

✅ **Use DFS when**:
1. **Detecting cycles**
2. **Topological sorting**
3. Finding **connected components**
4. **Path finding** (not necessarily shortest)
5. **Backtracking problems**
6. Tree/graph **traversals** where order doesn't matter

### DFS Applications

#### Application 1: Detect Cycle in Undirected Graph

```python
def has_cycle_undirected(graph, n):
    """
    Detect if undirected graph has a cycle
    
    Idea: During DFS, if we visit a node that's already visited
          and it's not the parent, there's a cycle
    """
    visited = set()
    
    def dfs(node, parent):
        visited.add(node)
        
        for neighbor in graph[node]:
            if neighbor not in visited:
                if dfs(neighbor, node):
                    return True
            elif neighbor != parent:
                # Visited and not parent = cycle!
                return True
        
        return False
    
    # Check all components
    for i in range(n):
        if i not in visited:
            if dfs(i, -1):
                return True
    
    return False

# Example with cycle
graph_cycle = {
    0: [1, 2],
    1: [0, 2],
    2: [0, 1]
}
print(has_cycle_undirected(graph_cycle, 3))  # True

# Example without cycle
graph_no_cycle = {
    0: [1, 2],
    1: [0],
    2: [0]
}
print(has_cycle_undirected(graph_no_cycle, 3))  # False
```

#### Application 2: Detect Cycle in Directed Graph

```python
def has_cycle_directed(graph, n):
    """
    Detect cycle in directed graph using DFS
    
    Uses 3 colors:
    - White (0): Unvisited
    - Gray (1): Currently in DFS path
    - Black (2): Completely processed
    
    If we reach a GRAY node, there's a cycle
    """
    color = [0] * n  # 0=white, 1=gray, 2=black
    
    def dfs(node):
        color[node] = 1  # Mark as in-progress
        
        for neighbor in graph.get(node, []):
            if color[neighbor] == 1:
                # Back edge to gray node = cycle!
                return True
            if color[neighbor] == 0:
                if dfs(neighbor):
                    return True
        
        color[node] = 2  # Mark as complete
        return False
    
    for i in range(n):
        if color[i] == 0:
            if dfs(i):
                return True
    
    return False

# Example
dag = {0: [1], 1: [2], 2: []}
print(has_cycle_directed(dag, 3))  # False

cyclic = {0: [1], 1: [2], 2: [0]}
print(has_cycle_directed(cyclic, 3))  # True
```

#### Application 3: Find All Paths

```python
def find_all_paths(graph, start, end, path=None):
    """
    Find all paths from start to end using DFS
    """
    if path is None:
        path = []
    
    path = path + [start]
    
    if start == end:
        return [path]
    
    paths = []
    for neighbor in graph.get(start, []):
        if neighbor not in path:  # Avoid cycles
            new_paths = find_all_paths(graph, neighbor, end, path)
            paths.extend(new_paths)
    
    return paths

# Example
graph_paths = {
    0: [1, 2],
    1: [3],
    2: [3],
    3: []
}
all_paths = find_all_paths(graph_paths, 0, 3)
print(all_paths)  # [[0, 1, 3], [0, 2, 3]]
```

---

## Common Graph Patterns

### Pattern 1: BFS for Shortest Path

**When**: Unweighted graph, find shortest distance/path

**Template**:
```python
def shortest_path_template(graph, start, target):
    queue = deque([(start, 0)])  # (node, distance)
    visited = {start}
    
    while queue:
        node, dist = queue.popleft()
        
        if node == target:
            return dist
        
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, dist + 1))
    
    return -1  # Not found
```

---

### Pattern 2: DFS for Path Exploration

**When**: Need to explore all possibilities, backtracking

**Template**:
```python
def dfs_explore_template(graph, node, visited, path):
    visited.add(node)
    path.append(node)
    
    # Process node
    # ...
    
    for neighbor in graph[node]:
        if neighbor not in visited:
            dfs_explore_template(graph, neighbor, visited, path)
    
    # Backtrack if needed
    path.pop()
```

---

### Pattern 3: Connected Components

**When**: Find separate groups in graph

**Template**:
```python
def count_components(graph, n):
    """Count number of connected components"""
    visited = set()
    count = 0
    
    def dfs(node):
        visited.add(node)
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                dfs(neighbor)
    
    for i in range(n):
        if i not in visited:
            dfs(i)
            count += 1
    
    return count
```

---

### Pattern 4: Island Problems (Grid DFS/BFS)

**When**: 2D grid treated as graph

**Template**:
```python
def num_islands(grid):
    """
    Count islands in 2D grid
    '1' = land, '0' = water
    """
    if not grid:
        return 0
    
    rows, cols = len(grid), len(grid[0])
    visited = set()
    count = 0
    
    def dfs(r, c):
        if (r < 0 or r >= rows or c < 0 or c >= cols or
            (r, c) in visited or grid[r][c] == '0'):
            return
        
        visited.add((r, c))
        # Explore 4 directions
        dfs(r + 1, c)
        dfs(r - 1, c)
        dfs(r, c + 1)
        dfs(r, c - 1)
    
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == '1' and (r, c) not in visited:
                dfs(r, c)
                count += 1
    
    return count

# Example
grid = [
    ['1', '1', '0', '0', '0'],
    ['1', '1', '0', '0', '0'],
    ['0', '0', '1', '0', '0'],
    ['0', '0', '0', '1', '1']
]
print(num_islands(grid))  # 3 islands
```

---

## Practice Problems

### Problem 1: Number of Provinces

**Problem**: Find number of provinces (connected components) where `isConnected[i][j] = 1` means cities i and j are connected.

```python
def findCircleNum(isConnected):
    """
    Input: Adjacency matrix
    Output: Number of connected components
    
    Time: O(n^2)
    Space: O(n)
    """
    n = len(isConnected)
    visited = set()
    
    def dfs(city):
        visited.add(city)
        for neighbor in range(n):
            if isConnected[city][neighbor] == 1 and neighbor not in visited:
                dfs(neighbor)
    
    provinces = 0
    for i in range(n):
        if i not in visited:
            dfs(i)
            provinces += 1
    
    return provinces

# Test
isConnected = [
    [1, 1, 0],
    [1, 1, 0],
    [0, 0, 1]
]
print(findCircleNum(isConnected))  # 2
```

### Problem 2: Clone Graph

**Problem**: Deep copy an undirected graph.

```python
class Node:
    def __init__(self, val=0, neighbors=None):
        self.val = val
        self.neighbors = neighbors if neighbors is not None else []

def cloneGraph(node):
    """
    Clone a graph using DFS
    
    Time: O(V + E)
    Space: O(V)
    """
    if not node:
        return None
    
    # Map original node to cloned node
    cloned = {}
    
    def dfs(original):
        if original in cloned:
            return cloned[original]
        
        # Clone node
        copy = Node(original.val)
        cloned[original] = copy
        
        # Clone neighbors
        for neighbor in original.neighbors:
            copy.neighbors.append(dfs(neighbor))
        
        return copy
    
    return dfs(node)
```

---

**Continue to Part 2** for advanced algorithms including:
- Topological Sort
- Dijkstra's Algorithm
- Bellman-Ford
- Floyd-Warshall
- Minimum Spanning Tree (Kruskal's, Prim's)
- Union-Find
- Advanced problems
