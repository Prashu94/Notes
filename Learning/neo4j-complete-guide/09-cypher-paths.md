# Chapter 9: Cypher - Working with Paths

## Learning Objectives
By the end of this chapter, you will:
- Understand path variables and path patterns
- Use variable-length relationships
- Find shortest paths between nodes
- Work with path functions and analysis
- Apply path patterns for complex traversals

---

## 9.1 Understanding Paths

### What is a Path?

A **path** is a sequence of alternating nodes and relationships, starting and ending with a node.

```
(Alice)-[:KNOWS]->(Bob)-[:KNOWS]->(Charlie)
```

This path has:
- 3 nodes: Alice, Bob, Charlie
- 2 relationships: both :KNOWS
- Length: 2 (number of relationships)

### Capturing Paths in Variables

```cypher
// Assign path to variable
MATCH path = (a:Person)-[:KNOWS]->(b:Person)-[:KNOWS]->(c:Person)
WHERE a.name = 'Alice'
RETURN path

// Path with multiple relationship types
MATCH path = (p:Person)-[:LIVES_IN|WORKS_IN]->(place)
RETURN path

// Named relationships in path
MATCH path = (a:Person)-[r1:KNOWS]->(b:Person)-[r2:KNOWS]->(c:Person)
RETURN path, r1.since, r2.since
```

---

## 9.2 Variable-Length Relationships

### Basic Variable-Length Patterns

```cypher
// Any length (1 or more hops)
MATCH (a:Person)-[:KNOWS*]->(b:Person)
WHERE a.name = 'Alice'
RETURN DISTINCT b.name

// Exactly N hops
MATCH (a:Person)-[:KNOWS*3]->(b:Person)  -- Exactly 3 hops
WHERE a.name = 'Alice'
RETURN b.name

// Range of hops
MATCH (a:Person)-[:KNOWS*1..3]->(b:Person)  -- 1 to 3 hops
WHERE a.name = 'Alice'
RETURN b.name, length(path. AS distance

// With path variable
MATCH path = (a:Person {name: 'Alice'})-[:KNOWS*1..4]->(b:Person)
RETURN b.name, length(path) AS distance
ORDER BY distance
```

### Variable-Length Syntax Options

```cypher
// Patterns:
// [*]      - 1 or more
// [*0..]   - 0 or more (optional path)
// [*..5]   - 1 to 5 (inclusive)
// [*2..5]  - 2 to 5 (inclusive)
// [*3]     - exactly 3
// [*0..1]  - optional single hop

// Optional relationship (0 or 1)
MATCH (a:Person)-[:MANAGES*0..1]->(b:Person)
WHERE a.name = 'Alice'
RETURN b.name  // Returns Alice and anyone she directly manages

// Zero or more (includes starting node)
MATCH (a:Person)-[:KNOWS*0..]->(b:Person)
WHERE a.name = 'Alice'
RETURN DISTINCT b.name  // Includes Alice herself
```

### Multiple Relationship Types

```cypher
// Variable length with multiple types
MATCH (a:Person)-[:KNOWS|FOLLOWS*1..3]->(b:Person)
WHERE a.name = 'Alice'
RETURN DISTINCT b.name

// Mixed directions
MATCH (a:Person)-[:KNOWS*1..3]-(b:Person)  -- Any direction
WHERE a.name = 'Alice'
RETURN DISTINCT b.name
```

### Performance Considerations

```cypher
// ⚠️ DANGER: Unbounded paths can be very slow!
// This could traverse the entire graph:
MATCH path = (a)-[*]->(b)  -- Don't do this!
RETURN path

// ✅ Always use upper bounds
MATCH path = (a:Person {name: 'Alice'})-[:KNOWS*..6]->(b:Person)
RETURN b.name

// ✅ Use relationship direction when possible
MATCH (a:Person {name: 'Alice'})-[:REPORTS_TO*1..5]->(manager:Person)
RETURN manager.name
```

---

## 9.3 Path Functions

### Basic Path Functions

```cypher
// Get all path components
MATCH path = (a:Person {name: 'Alice'})-[:KNOWS*1..3]->(b:Person)
RETURN 
    path,
    nodes(path) AS allNodes,
    relationships(path) AS allRels,
    length(path) AS pathLength

// Extract specific elements
MATCH path = (a:Person {name: 'Alice'})-[:KNOWS*]->(b:Person {name: 'Diana'})
RETURN 
    nodes(path)[0].name AS start,
    nodes(path)[-1].name AS end,
    [n IN nodes(path) | n.name] AS namesList
```

### Working with nodes() and relationships()

```cypher
// Get node names from path
MATCH path = (a:Person {name: 'Alice'})-[:KNOWS*1..4]->(b:Person)
WITH path, [n IN nodes(path) | n.name] AS names
RETURN names

// Get relationship properties
MATCH path = (a:Person {name: 'Alice'})-[:KNOWS*1..3]->(b:Person)
WITH path, relationships(path) AS rels
RETURN [r IN rels | r.since] AS connectionDates

// Sum relationship weights
MATCH path = (a:City {name: 'NYC'})-[:ROAD*]->(b:City {name: 'LA'})
WITH path, relationships(path) AS roads
RETURN 
    path,
    reduce(total = 0, r IN roads | total + r.distance) AS totalDistance
ORDER BY totalDistance
LIMIT 5
```

### length() Function

```cypher
// Path length = number of relationships
MATCH path = (a:Person)-[:KNOWS*]->(b:Person)
WHERE a.name = 'Alice' AND b.name = 'Diana'
RETURN length(path) AS hops

// Filter by path length
MATCH path = (a:Person {name: 'Alice'})-[:KNOWS*]->(b:Person)
WHERE length(path) <= 3
RETURN b.name, length(path) AS distance

// Group by distance
MATCH path = (a:Person {name: 'Alice'})-[:KNOWS*1..5]->(b:Person)
RETURN length(path) AS distance, count(DISTINCT b) AS peopleAtDistance
ORDER BY distance
```

---

## 9.4 Shortest Path Algorithms

### shortestPath()

```cypher
// Find single shortest path
MATCH path = shortestPath(
    (a:Person {name: 'Alice'})-[:KNOWS*]-(b:Person {name: 'Diana'})
)
RETURN path, length(path) AS distance

// Shortest path with relationship type
MATCH path = shortestPath(
    (a:Person {name: 'Alice'})-[:KNOWS|FOLLOWS*]-(b:Person {name: 'Diana'})
)
RETURN path

// With upper bound (recommended)
MATCH path = shortestPath(
    (a:Person {name: 'Alice'})-[:KNOWS*..10]-(b:Person {name: 'Diana'})
)
RETURN path
```

### allShortestPaths()

```cypher
// Find ALL paths of shortest length
MATCH path = allShortestPaths(
    (a:Person {name: 'Alice'})-[:KNOWS*]-(b:Person {name: 'Diana'})
)
RETURN path, length(path) AS distance

// Multiple shortest paths analysis
MATCH path = allShortestPaths(
    (a:Person {name: 'Alice'})-[:KNOWS*..6]-(b:Person {name: 'Diana'})
)
WITH path, [n IN nodes(path) | n.name] AS route
RETURN route, length(path) AS distance
```

### Shortest Path with Conditions

```cypher
// Filter shortest path with WHERE
MATCH path = shortestPath(
    (a:Person {name: 'Alice'})-[:KNOWS*]-(b:Person {name: 'Diana'})
)
WHERE all(r IN relationships(path) WHERE r.since > 2015)
RETURN path

// Shortest path avoiding certain nodes
MATCH path = shortestPath(
    (a:Person {name: 'Alice'})-[:KNOWS*..10]-(b:Person {name: 'Diana'})
)
WHERE none(n IN nodes(path) WHERE n.name = 'Bob')
RETURN path

// Shortest path through specific intermediate
MATCH 
    path1 = shortestPath((a:Person {name: 'Alice'})-[:KNOWS*]-(mid:Person {name: 'Charlie'})),
    path2 = shortestPath((mid)-[:KNOWS*]-(b:Person {name: 'Diana'}))
RETURN length(path1) + length(path2) AS totalDistance
```

---

## 9.5 Weighted Shortest Paths

### Using APOC for Weighted Paths

```cypher
// Dijkstra's algorithm (requires APOC)
MATCH (start:City {name: 'NYC'}), (end:City {name: 'LA'})
CALL apoc.algo.dijkstra(start, end, 'ROAD', 'distance')
YIELD path, weight
RETURN path, weight AS totalDistance

// A* algorithm with coordinates
MATCH (start:City {name: 'NYC'}), (end:City {name: 'LA'})
CALL apoc.algo.aStar(start, end, 'ROAD', 'distance', 'lat', 'lon')
YIELD path, weight
RETURN path, weight
```

### Manual Weighted Path Finding

```cypher
// Find paths and calculate weights manually
MATCH path = (a:City {name: 'NYC'})-[:ROAD*..5]->(b:City {name: 'LA'})
WITH path, reduce(dist = 0, r IN relationships(path) | dist + r.distance) AS totalDistance
RETURN path, totalDistance
ORDER BY totalDistance
LIMIT 1

// Weighted path with multiple criteria
MATCH path = (a:City {name: 'NYC'})-[:ROAD*..6]->(b:City {name: 'LA'})
WITH path,
     reduce(d = 0, r IN relationships(path) | d + r.distance) AS distance,
     reduce(t = 0, r IN relationships(path) | t + r.time) AS time
RETURN path, distance, time
ORDER BY distance + time * 10  // Weighted combination
LIMIT 5
```

---

## 9.6 Path Pattern Expressions

### Quantified Path Patterns (Neo4j 5+)

```cypher
// Repeat a pattern N times
MATCH (p:Person)-[:KNOWS]->{3}(friend:Person)  -- Exactly 3 KNOWS
WHERE p.name = 'Alice'
RETURN friend.name

// Range repetition
MATCH (p:Person)-[:KNOWS]->{1,4}(friend:Person)  -- 1 to 4 times
WHERE p.name = 'Alice'
RETURN DISTINCT friend.name

// Zero or more
MATCH (p:Person)-[:KNOWS]->*(friend:Person)  -- 0 or more
WHERE p.name = 'Alice'
RETURN DISTINCT friend.name

// One or more
MATCH (p:Person)-[:KNOWS]->{1,}(friend:Person)  -- 1 or more
WHERE p.name = 'Alice'
RETURN DISTINCT friend.name
```

### Quantified Patterns with Complex Paths

```cypher
// Pattern with inline conditions
MATCH (p:Person WHERE p.age > 25)-[:KNOWS]->{1,3}(friend:Person WHERE friend.city = 'NYC')
RETURN p.name, friend.name

// Multiple relationship pattern
MATCH (a:Person)-[:KNOWS]->()-[:WORKS_AT]->(c:Company)
WHERE a.name = 'Alice'
RETURN DISTINCT c.name

// Quantified with grouping
MATCH (a:Person {name: 'Alice'})(()-[:KNOWS]->())+(b:Person)
RETURN DISTINCT b.name
```

---

## 9.7 Cycles and Path Uniqueness

### Detecting Cycles

```cypher
// Find cycles in relationships
MATCH path = (n:Person)-[:KNOWS*3..6]->(n)
RETURN path, [node IN nodes(path) | node.name] AS cycle
LIMIT 10

// Specific cycle starting from a node
MATCH path = (a:Person {name: 'Alice'})-[:KNOWS*2..5]->(a)
RETURN [n IN nodes(path) | n.name] AS cycleMembers

// Detect any cycles involving a node
MATCH (a:Person {name: 'Alice'})
WHERE EXISTS { (a)-[:KNOWS*2..]->(a) }
RETURN a.name AS hasCycle
```

### Path Uniqueness Rules

```cypher
// By default, relationships are not repeated in a path
// This prevents infinite loops

// Find distinct paths (no repeated relationships)
MATCH path = (a:Person {name: 'Alice'})-[:KNOWS*1..4]->(b:Person)
RETURN path

// Allow node repetition (but not relationship)
MATCH path = (a:Person {name: 'Alice'})-[:KNOWS*1..4]->(b:Person)
WHERE size(nodes(path)) <> size(apoc.coll.toSet([n IN nodes(path) | id(n)]))
RETURN path  // Paths that visit some nodes multiple times
```

### Acyclic Paths

```cypher
// Ensure no repeated nodes (truly acyclic)
MATCH path = (a:Person {name: 'Alice'})-[:KNOWS*1..5]->(b:Person)
WHERE size(nodes(path)) = size(apoc.coll.toSet([n IN nodes(path) | id(n)]))
RETURN path, [n IN nodes(path) | n.name] AS route

// Alternative using all() predicate
MATCH path = (a:Person {name: 'Alice'})-[:KNOWS*1..5]->(b:Person)
WITH path, nodes(path) AS pathNodes
WHERE all(i IN range(0, size(pathNodes)-2) WHERE 
      NOT pathNodes[i] IN pathNodes[i+1..])
RETURN path
```

---

## 9.8 Advanced Path Patterns

### Multi-Hop with Intermediate Nodes

```cypher
// Capture intermediate nodes
MATCH (a:Person {name: 'Alice'})-[:KNOWS*1..3]->(b:Person)
WITH a, b, 
     [(a)-[:KNOWS*1..3]->(intermediate:Person)-[:KNOWS]->(b) | intermediate.name] AS intermediates
RETURN b.name, intermediates

// Find paths through specific intermediates
MATCH (a:Person {name: 'Alice'})-[:KNOWS*]->(mid:Person)-[:KNOWS*]->(b:Person {name: 'Diana'})
WHERE mid.department = 'Engineering'
RETURN [a.name, mid.name, b.name] AS route
```

### Bidirectional Traversal

```cypher
// Search from both ends
MATCH path = (a:Person {name: 'Alice'})-[:KNOWS*1..5]-(b:Person {name: 'Diana'})
RETURN path
// Engine may use bidirectional search optimization
```

### Path with Aggregations

```cypher
// Aggregate over paths
MATCH path = (a:Person {name: 'Alice'})-[:KNOWS*1..4]->(b:Person)
WITH b, min(length(path)) AS shortestDistance
RETURN b.name, shortestDistance
ORDER BY shortestDistance

// Count paths of each length
MATCH path = (a:Person {name: 'Alice'})-[:KNOWS*1..5]->(b:Person)
RETURN length(path) AS distance, count(path) AS pathCount
ORDER BY distance

// Find all reachable nodes with their shortest distance
MATCH path = (a:Person {name: 'Alice'})-[:KNOWS*1..6]->(b:Person)
WITH b, min(length(path)) AS distance
RETURN b.name, distance
ORDER BY distance
```

---

## 9.9 Common Path Patterns

### Friend-of-Friend

```cypher
// Friends of friends (excluding direct friends)
MATCH (me:Person {name: 'Alice'})-[:KNOWS]->(friend)-[:KNOWS]->(fof:Person)
WHERE NOT (me)-[:KNOWS]->(fof)
  AND me <> fof
RETURN DISTINCT fof.name AS friendOfFriend, count(friend) AS mutualFriends
ORDER BY mutualFriends DESC
```

### Degrees of Separation

```cypher
// Find degree of separation between two people
MATCH path = shortestPath(
    (a:Person {name: 'Alice'})-[:KNOWS*]-(b:Person {name: 'Diana'})
)
RETURN length(path) AS degreesOfSeparation

// Distribution of degrees of separation from one person
MATCH (me:Person {name: 'Alice'})
MATCH path = shortestPath((me)-[:KNOWS*..6]-(other:Person))
WHERE me <> other
RETURN length(path) AS degree, count(other) AS people
ORDER BY degree
```

### Influence Paths

```cypher
// Find how information might spread
MATCH path = (source:Person {name: 'Alice'})-[:FOLLOWS*1..4]->(reached:Person)
WITH reached, min(length(path)) AS hops
RETURN hops, count(reached) AS reachable
ORDER BY hops
```

### Supply Chain / Dependency Analysis

```cypher
// Find all dependencies (transitive)
MATCH path = (service:Service {name: 'WebApp'})-[:DEPENDS_ON*]->(dependency:Service)
RETURN DISTINCT dependency.name, length(path) AS depth
ORDER BY depth

// Find critical paths
MATCH path = (start:Service {name: 'WebApp'})-[:DEPENDS_ON*]->(end:Service {name: 'Database'})
RETURN path, [n IN nodes(path) | n.name] AS dependencyChain
```

---

## 9.10 Python Examples

### Path Traversal

```python
from neo4j import GraphDatabase

URI = "neo4j://localhost:7687"
AUTH = ("neo4j", "password")

def find_shortest_path(driver, from_name: str, to_name: str):
    with driver.session() as session:
        result = session.run("""
            MATCH path = shortestPath(
                (a:Person {name: $from})-[:KNOWS*..10]-(b:Person {name: $to})
            )
            RETURN path, 
                   [n IN nodes(path) | n.name] AS route,
                   length(path) AS distance
        """, from_name=from_name, to_name=to_name)
        
        record = result.single()
        if record:
            print(f"Shortest path from {from_name} to {to_name}:")
            print(f"  Route: {' -> '.join(record['route'])}")
            print(f"  Distance: {record['distance']} hops")
        else:
            print(f"No path found between {from_name} and {to_name}")

def find_all_reachable(driver, start_name: str, max_hops: int = 5):
    with driver.session() as session:
        result = session.run("""
            MATCH path = (start:Person {name: $name})-[:KNOWS*1..$maxHops]->(reachable:Person)
            WITH reachable, min(length(path)) AS distance
            RETURN reachable.name AS name, distance
            ORDER BY distance, name
        """, name=start_name, maxHops=max_hops)
        
        print(f"\nPeople reachable from {start_name} (max {max_hops} hops):")
        for record in result:
            print(f"  {record['name']} - {record['distance']} hop(s)")

def analyze_path_weights(driver, from_city: str, to_city: str):
    with driver.session() as session:
        result = session.run("""
            MATCH path = (a:City {name: $from})-[:ROAD*..8]->(b:City {name: $to})
            WITH path, 
                 reduce(dist = 0, r IN relationships(path) | dist + r.distance) AS totalDist,
                 [n IN nodes(path) | n.name] AS route
            RETURN route, totalDist
            ORDER BY totalDist
            LIMIT 5
        """, from_city=from_city, to_city=to_city)
        
        print(f"\nTop 5 shortest routes from {from_city} to {to_city}:")
        for i, record in enumerate(result, 1):
            print(f"  {i}. {' -> '.join(record['route'])} ({record['totalDist']} km)")

with GraphDatabase.driver(URI, auth=AUTH) as driver:
    find_shortest_path(driver, "Alice", "Diana")
    find_all_reachable(driver, "Alice", 4)
    analyze_path_weights(driver, "NYC", "LA")
```

---

## Summary

### Key Takeaways

1. **Path Variables**: Capture entire paths with `path = (a)-[:REL]->(b)`
2. **Variable-Length**: Use `*min..max` for flexible path lengths
3. **Path Functions**: `nodes()`, `relationships()`, `length()`
4. **Shortest Paths**: `shortestPath()` and `allShortestPaths()`
5. **Performance**: Always use upper bounds on variable-length paths

### Quick Reference

```cypher
-- Capture path
MATCH path = (a)-[:REL*]->(b)
RETURN nodes(path), relationships(path), length(path)

-- Variable length options
[*]         -- 1 or more
[*0..]      -- 0 or more  
[*1..5]     -- 1 to 5
[*3]        -- exactly 3

-- Shortest path
shortestPath((a)-[:REL*]-(b))
allShortestPaths((a)-[:REL*]-(b))

-- Path weight calculation
reduce(total = 0, r IN relationships(path) | total + r.weight)
```

---

## Exercises

### Exercise 9.1: Basic Paths
1. Find all paths between two people up to 4 hops
2. Return the names of all nodes in each path
3. Filter paths where all relationships were created after 2020

### Exercise 9.2: Shortest Paths
1. Find the shortest path between two specific nodes
2. Find all shortest paths and compare the routes
3. Find shortest path that goes through a specific intermediate node

### Exercise 9.3: Variable-Length Patterns
1. Find all people within 3 hops of a starting person
2. Group the results by distance (1 hop, 2 hops, 3 hops)
3. Exclude direct connections to find only indirect connections

### Exercise 9.4: Weighted Paths
1. Calculate the total cost of each path in a routing graph
2. Find the path with minimum total cost
3. Find paths where the cost is within 20% of the optimal

---

**Next Chapter: [Chapter 10: Cypher - Subqueries and UNION](10-cypher-subqueries.md)**
