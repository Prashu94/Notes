# Chapter 13: Cypher - List Operations

## Learning Objectives
By the end of this chapter, you will:
- Master list creation and manipulation
- Use list comprehensions effectively
- Apply UNWIND for list processing
- Work with REDUCE for aggregations
- Handle nested lists and complex transformations

---

## 13.1 Creating Lists

### Literal Lists

```cypher
// Basic lists
RETURN [1, 2, 3, 4, 5] AS numbers
RETURN ['apple', 'banana', 'cherry'] AS fruits
RETURN [true, false, true] AS booleans

// Mixed types (allowed but not recommended)
RETURN [1, 'two', 3.0, null] AS mixed

// Empty list
RETURN [] AS empty

// Nested lists
RETURN [[1, 2], [3, 4], [5, 6]] AS matrix
```

### Range Function

```cypher
// Basic range (inclusive)
RETURN range(1, 5) AS oneToFive      // [1, 2, 3, 4, 5]
RETURN range(0, 10, 2) AS evens      // [0, 2, 4, 6, 8, 10]
RETURN range(10, 1, -1) AS countdown // [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]

// Generate dates
WITH range(0, 6) AS days
RETURN [d IN days | date() + duration({days: d})] AS nextWeek

// Index generation
WITH ['a', 'b', 'c', 'd'] AS items
RETURN [i IN range(0, size(items)-1) | {index: i, value: items[i]}] AS indexed
```

### COLLECT Aggregation

```cypher
// Collect from query results
MATCH (p:Person)
RETURN collect(p.name) AS allNames

// Collect with ordering
MATCH (p:Person)
WITH p ORDER BY p.name
RETURN collect(p.name) AS sortedNames

// Collect distinct values
MATCH (p:Person)
RETURN collect(DISTINCT p.city) AS uniqueCities

// Collect maps
MATCH (p:Person)
RETURN collect({name: p.name, age: p.age}) AS people

// Collect with grouping
MATCH (e:Employee)
RETURN e.department, collect(e.name) AS employees
```

---

## 13.2 Accessing List Elements

### Index-Based Access

```cypher
// Single element (0-indexed)
WITH ['a', 'b', 'c', 'd', 'e'] AS list
RETURN 
    list[0] AS first,       // 'a'
    list[2] AS third,       // 'c'
    list[-1] AS last,       // 'e'
    list[-2] AS secondLast  // 'd'

// Out of bounds returns null
WITH [1, 2, 3] AS list
RETURN list[10] AS outOfBounds  // null
```

### Slicing

```cypher
WITH ['a', 'b', 'c', 'd', 'e'] AS list
RETURN 
    list[1..3] AS slice,      // ['b', 'c'] (exclusive end)
    list[2..] AS fromIndex,   // ['c', 'd', 'e']
    list[..3] AS toIndex,     // ['a', 'b', 'c']
    list[-3..] AS lastThree,  // ['c', 'd', 'e']
    list[..-2] AS dropLast2   // ['a', 'b', 'c']

// Pagination pattern
WITH range(1, 100) AS allItems
WITH allItems[20..30] AS page3  // Items 21-30 (page 3, size 10)
RETURN page3
```

### HEAD, LAST, TAIL

```cypher
WITH [1, 2, 3, 4, 5] AS list
RETURN 
    head(list) AS first,      // 1
    last(list) AS last,       // 5
    tail(list) AS rest        // [2, 3, 4, 5]

// Safe access with empty list
WITH [] AS empty
RETURN 
    head(empty) AS first,     // null
    last(empty) AS last,      // null
    tail(empty) AS rest       // []
```

---

## 13.3 List Comprehensions

### Basic Transformation

```cypher
// Transform each element
WITH [1, 2, 3, 4, 5] AS numbers
RETURN [n IN numbers | n * 2] AS doubled
// [2, 4, 6, 8, 10]

// String transformation
WITH ['alice', 'bob', 'charlie'] AS names
RETURN [name IN names | toUpper(name)] AS upper
// ['ALICE', 'BOB', 'CHARLIE']

// Create maps from values
WITH [1, 2, 3] AS ids
RETURN [id IN ids | {id: id, active: true}] AS objects
```

### Filtering

```cypher
// Filter only
WITH [1, 2, 3, 4, 5, 6, 7, 8, 9, 10] AS numbers
RETURN [n IN numbers WHERE n % 2 = 0] AS evens
// [2, 4, 6, 8, 10]

// Multiple conditions
WITH range(1, 20) AS numbers
RETURN [n IN numbers WHERE n % 2 = 0 AND n % 3 = 0] AS divisibleBy6
// [6, 12, 18]

// Filter with string operations
WITH ['apple', 'apricot', 'banana', 'avocado'] AS fruits
RETURN [f IN fruits WHERE f STARTS WITH 'a'] AS aFruits
// ['apple', 'apricot', 'avocado']
```

### Filter and Transform Combined

```cypher
// Filter then transform
WITH [1, 2, 3, 4, 5] AS numbers
RETURN [n IN numbers WHERE n > 2 | n * 10] AS result
// [30, 40, 50]

// Complex transformation
MATCH (p:Person)
WITH collect(p) AS people
RETURN [person IN people WHERE person.age >= 18 | 
    {name: person.name, status: 'adult'}
] AS adults

// Nested property access
WITH [{name: 'Alice', score: 85}, {name: 'Bob', score: 92}, {name: 'Charlie', score: 78}] AS students
RETURN [s IN students WHERE s.score >= 80 | s.name] AS passing
// ['Alice', 'Bob']
```

### Nested Comprehensions

```cypher
// Matrix operations
WITH [[1, 2, 3], [4, 5, 6], [7, 8, 9]] AS matrix
RETURN [row IN matrix | [n IN row | n * 2]] AS doubled
// [[2, 4, 6], [8, 10, 12], [14, 16, 18]]

// Flatten with nested comprehension
WITH [[1, 2], [3, 4], [5, 6]] AS nested
WITH [row IN nested | [x IN row | x]] AS same
RETURN reduce(flat = [], row IN same | flat + row) AS flattened
// [1, 2, 3, 4, 5, 6]
```

---

## 13.4 UNWIND

### Basic UNWIND

```cypher
// Convert list to rows
UNWIND [1, 2, 3] AS num
RETURN num
// Returns 3 rows: 1, 2, 3

// With source list
WITH ['Alice', 'Bob', 'Charlie'] AS names
UNWIND names AS name
RETURN name
```

### UNWIND for Batch Operations

```cypher
// Create multiple nodes
UNWIND ['Alice', 'Bob', 'Charlie'] AS name
CREATE (p:Person {name: name})
RETURN p.name

// Create from parameter list
:params {people: [{name: 'Alice', age: 30}, {name: 'Bob', age: 25}]}

UNWIND $people AS person
CREATE (p:Person {name: person.name, age: person.age})
RETURN count(p) AS created

// Create relationships in batch
UNWIND [
    {from: 'Alice', to: 'Bob'},
    {from: 'Bob', to: 'Charlie'},
    {from: 'Charlie', to: 'Alice'}
] AS rel
MATCH (a:Person {name: rel.from}), (b:Person {name: rel.to})
CREATE (a)-[:KNOWS]->(b)
```

### UNWIND with Index

```cypher
// Add index to each element
WITH ['a', 'b', 'c', 'd'] AS items
UNWIND range(0, size(items)-1) AS idx
RETURN idx, items[idx] AS item

// Alternative using reduce
WITH ['a', 'b', 'c', 'd'] AS items
RETURN [i IN range(0, size(items)-1) | {index: i, value: items[i]}] AS indexed
```

### Handling Empty Lists

```cypher
// UNWIND on empty list returns no rows
UNWIND [] AS item
RETURN item  // No results

// Preserve rows when list might be empty
WITH [] AS items
UNWIND (CASE WHEN size(items) = 0 THEN [null] ELSE items END) AS item
RETURN item  // Returns one row with null

// Alternative: OPTIONAL MATCH pattern
MATCH (p:Person)
OPTIONAL MATCH (p)-[:PURCHASED]->(product:Product)
RETURN p.name, collect(product.name) AS products
// Returns empty list [] instead of no row
```

---

## 13.5 REDUCE Function

### Basic REDUCE

```cypher
// Sum of numbers
WITH [1, 2, 3, 4, 5] AS numbers
RETURN reduce(sum = 0, n IN numbers | sum + n) AS total
// 15

// Product of numbers
WITH [1, 2, 3, 4, 5] AS numbers
RETURN reduce(product = 1, n IN numbers | product * n) AS factorial
// 120

// String concatenation
WITH ['Hello', ' ', 'World', '!'] AS words
RETURN reduce(str = '', w IN words | str + w) AS sentence
// 'Hello World!'
```

### Accumulating Objects

```cypher
// Build a map
WITH [['a', 1], ['b', 2], ['c', 3]] AS pairs
RETURN reduce(
    map = {}, 
    pair IN pairs | 
    apoc.map.setKey(map, pair[0], pair[1])
) AS result
// {a: 1, b: 2, c: 3}

// Running total
WITH [10, 20, 30, 40] AS amounts
WITH [i IN range(0, size(amounts)-1) | 
    reduce(sum = 0, j IN range(0, i) | sum + amounts[j])
] AS runningTotals
RETURN runningTotals
// [10, 30, 60, 100]
```

### Complex Reductions

```cypher
// Find maximum
WITH [3, 1, 4, 1, 5, 9, 2, 6] AS numbers
RETURN reduce(
    maxVal = head(numbers), 
    n IN numbers | 
    CASE WHEN n > maxVal THEN n ELSE maxVal END
) AS maximum
// 9

// Count occurrences
WITH ['a', 'b', 'a', 'c', 'a', 'b'] AS items
RETURN reduce(
    counts = {}, 
    item IN items | 
    apoc.map.setKey(counts, item, coalesce(counts[item], 0) + 1)
) AS frequency
// {a: 3, b: 2, c: 1}
```

### Path Weight Calculation

```cypher
// Sum relationship weights in a path
MATCH path = (a:City {name: 'NYC'})-[:ROAD*]->(b:City {name: 'LA'})
WITH path, relationships(path) AS roads
RETURN 
    [n IN nodes(path) | n.name] AS route,
    reduce(total = 0, r IN roads | total + r.distance) AS totalDistance
ORDER BY totalDistance
LIMIT 5
```

---

## 13.6 List Functions

### Size and Empty Checks

```cypher
WITH [1, 2, 3] AS list
RETURN 
    size(list) AS length,           // 3
    size(list) = 0 AS isEmpty,      // false
    size(list) > 0 AS hasElements   // true
```

### REVERSE and SORT

```cypher
// Reverse
RETURN reverse([1, 2, 3, 4, 5]) AS reversed
// [5, 4, 3, 2, 1]

// Sort (using collect with ORDER BY)
UNWIND [3, 1, 4, 1, 5, 9, 2, 6] AS n
WITH n ORDER BY n
RETURN collect(n) AS sorted
// [1, 1, 2, 3, 4, 5, 6, 9]

// Sort descending
UNWIND [3, 1, 4, 1, 5, 9, 2, 6] AS n
WITH n ORDER BY n DESC
RETURN collect(n) AS sortedDesc
```

### APOC Collection Functions

```cypher
// Sort list directly (APOC)
RETURN apoc.coll.sort([3, 1, 4, 1, 5]) AS sorted
// [1, 1, 3, 4, 5]

// Sort objects by property
WITH [{name: 'Charlie', age: 30}, {name: 'Alice', age: 25}, {name: 'Bob', age: 35}] AS people
RETURN apoc.coll.sortMaps(people, 'name') AS byName

// Remove duplicates
RETURN apoc.coll.toSet([1, 2, 2, 3, 3, 3]) AS unique
// [1, 2, 3]

// Flatten nested lists
RETURN apoc.coll.flatten([[1, 2], [3, 4], [5]]) AS flat
// [1, 2, 3, 4, 5]

// Shuffle
RETURN apoc.coll.shuffle([1, 2, 3, 4, 5]) AS shuffled

// Random sample
RETURN apoc.coll.randomItems([1, 2, 3, 4, 5], 3) AS sample
```

### Set Operations

```cypher
// Union (combine unique)
WITH [1, 2, 3] AS a, [3, 4, 5] AS b
RETURN apoc.coll.union(a, b) AS union
// [1, 2, 3, 4, 5]

// Intersection (common elements)
WITH [1, 2, 3, 4] AS a, [3, 4, 5, 6] AS b
RETURN apoc.coll.intersection(a, b) AS common
// [3, 4]

// Difference (subtract)
WITH [1, 2, 3, 4] AS a, [3, 4] AS b
RETURN apoc.coll.subtract(a, b) AS diff
// [1, 2]

// Symmetric difference (XOR)
WITH [1, 2, 3] AS a, [3, 4, 5] AS b
RETURN apoc.coll.disjunction(a, b) AS xor
// [1, 2, 4, 5]
```

---

## 13.7 List Predicates

### ANY, ALL, NONE, SINGLE

```cypher
WITH [1, 2, 3, 4, 5] AS numbers

// ANY: at least one matches
RETURN any(n IN numbers WHERE n > 4) AS hasLarge  // true

// ALL: every element matches
RETURN all(n IN numbers WHERE n > 0) AS allPositive  // true

// NONE: no element matches
RETURN none(n IN numbers WHERE n < 0) AS noNegatives  // true

// SINGLE: exactly one matches
RETURN single(n IN numbers WHERE n = 3) AS hasExactlyOneThree  // true
```

### Practical Predicate Usage

```cypher
// Find people with all required skills
MATCH (p:Person)
WHERE all(skill IN ['Python', 'SQL'] WHERE skill IN p.skills)
RETURN p.name AS fullStack

// Find orders with any out-of-stock item
MATCH (o:Order)-[:CONTAINS]->(p:Product)
WITH o, collect(p) AS products
WHERE any(prod IN products WHERE prod.stock = 0)
RETURN o.id AS backorderedOrders

// Find paths where all relationships are recent
MATCH path = (a:Person)-[:KNOWS*1..4]->(b:Person)
WHERE all(r IN relationships(path) WHERE r.since > 2020)
RETURN path
```

---

## 13.8 Working with Nested Lists

### Flattening

```cypher
// Manual flatten (one level)
WITH [[1, 2], [3, 4], [5, 6]] AS nested
RETURN reduce(flat = [], inner IN nested | flat + inner) AS flattened
// [1, 2, 3, 4, 5, 6]

// APOC deep flatten
WITH [[1, [2, 3]], [[4, 5], 6]] AS deepNested
RETURN apoc.coll.flatten(deepNested, true) AS fullyFlat
// [1, 2, 3, 4, 5, 6]
```

### Grouping into Nested Lists

```cypher
// Partition into chunks
WITH range(1, 10) AS numbers
RETURN apoc.coll.partition(numbers, 3) AS chunks
// [[1, 2, 3], [4, 5, 6], [7, 8, 9], [10]]

// Group by property
MATCH (p:Person)
WITH p.department AS dept, collect(p.name) AS employees
RETURN collect({department: dept, employees: employees}) AS grouped
```

### Matrix Operations

```cypher
// Transpose matrix
WITH [[1, 2, 3], [4, 5, 6], [7, 8, 9]] AS matrix
WITH range(0, size(matrix[0])-1) AS cols
RETURN [c IN cols | [r IN matrix | r[c]]] AS transposed
// [[1, 4, 7], [2, 5, 8], [3, 6, 9]]

// Matrix multiplication (simplified 2x2)
WITH [[1, 2], [3, 4]] AS A, [[5, 6], [7, 8]] AS B
RETURN [
    [A[0][0]*B[0][0] + A[0][1]*B[1][0], A[0][0]*B[0][1] + A[0][1]*B[1][1]],
    [A[1][0]*B[0][0] + A[1][1]*B[1][0], A[1][0]*B[0][1] + A[1][1]*B[1][1]]
] AS result
// [[19, 22], [43, 50]]
```

---

## 13.9 Practical Patterns

### Building Adjacency Lists

```cypher
// Get neighbors for each node
MATCH (p:Person)-[:KNOWS]->(friend:Person)
WITH p, collect(friend.name) AS friends
RETURN p.name AS person, friends
ORDER BY size(friends) DESC
```

### Pagination with Lists

```cypher
// Get a specific page from results
:params {pageSize: 10, pageNumber: 3}

MATCH (p:Product)
WITH p ORDER BY p.name
WITH collect(p) AS allProducts
WITH allProducts[($pageNumber-1) * $pageSize .. $pageNumber * $pageSize] AS page,
     size(allProducts) AS total
UNWIND page AS product
RETURN product.name, total
```

### Tag/Keyword Processing

```cypher
// Normalize and deduplicate tags
WITH ['Python', 'python', 'PYTHON', 'Java', 'java'] AS tags
WITH [t IN tags | toLower(trim(t))] AS normalized
RETURN apoc.coll.toSet(normalized) AS uniqueTags
// ['python', 'java']

// Find items with overlapping tags
MATCH (p1:Post), (p2:Post)
WHERE p1 <> p2
WITH p1, p2, 
     apoc.coll.intersection(p1.tags, p2.tags) AS commonTags
WHERE size(commonTags) >= 2
RETURN p1.title, p2.title, commonTags
```

### Time Series Data

```cypher
// Calculate moving average
WITH [10, 20, 30, 40, 50, 60, 70] AS values
WITH values, 3 AS window
RETURN [i IN range(window-1, size(values)-1) | 
    reduce(sum = 0.0, j IN range(i-window+1, i) | sum + values[j]) / window
] AS movingAverage
// [20.0, 30.0, 40.0, 50.0, 60.0]
```

---

## 13.10 Python Examples

### List Processing

```python
from neo4j import GraphDatabase

URI = "neo4j://localhost:7687"
AUTH = ("neo4j", "password")

def batch_create_with_unwind(driver, items: list):
    """Create multiple nodes using UNWIND."""
    with driver.session() as session:
        result = session.run("""
            UNWIND $items AS item
            CREATE (p:Product {
                name: item.name,
                price: item.price,
                tags: item.tags
            })
            RETURN count(p) AS created
        """, items=items)
        
        return result.single()['created']

def find_similar_products(driver, product_name: str, min_common_tags: int = 2):
    """Find products with overlapping tags."""
    with driver.session() as session:
        result = session.run("""
            MATCH (p1:Product {name: $name}), (p2:Product)
            WHERE p1 <> p2
            WITH p1, p2, 
                 [t IN p1.tags WHERE t IN p2.tags] AS commonTags
            WHERE size(commonTags) >= $minCommon
            RETURN p2.name AS product, commonTags
            ORDER BY size(commonTags) DESC
        """, name=product_name, minCommon=min_common_tags)
        
        return [(r['product'], r['commonTags']) for r in result]

def get_paginated_results(driver, page: int, page_size: int):
    """Get paginated products using list slicing."""
    with driver.session() as session:
        result = session.run("""
            MATCH (p:Product)
            WITH p ORDER BY p.name
            WITH collect(p) AS all, count(p) AS total
            RETURN 
                all[($page-1) * $pageSize .. $page * $pageSize] AS products,
                total,
                toInteger(ceil(toFloat(total) / $pageSize)) AS totalPages
        """, page=page, pageSize=page_size)
        
        record = result.single()
        return {
            'products': [dict(p) for p in record['products']],
            'total': record['total'],
            'totalPages': record['totalPages'],
            'currentPage': page
        }

def calculate_path_metrics(driver, start: str, end: str):
    """Calculate metrics across paths."""
    with driver.session() as session:
        result = session.run("""
            MATCH path = (a:City {name: $start})-[:ROAD*..6]->(b:City {name: $end})
            WITH path,
                 [n IN nodes(path) | n.name] AS route,
                 reduce(dist = 0, r IN relationships(path) | dist + r.distance) AS totalDist,
                 reduce(time = 0, r IN relationships(path) | time + r.time) AS totalTime
            RETURN route, totalDist, totalTime
            ORDER BY totalDist
            LIMIT 5
        """, start=start, end=end)
        
        return [dict(r) for r in result]

# Usage
with GraphDatabase.driver(URI, auth=AUTH) as driver:
    # Batch create
    products = [
        {'name': 'Laptop', 'price': 999, 'tags': ['electronics', 'computer']},
        {'name': 'Phone', 'price': 699, 'tags': ['electronics', 'mobile']},
        {'name': 'Tablet', 'price': 499, 'tags': ['electronics', 'mobile', 'computer']}
    ]
    count = batch_create_with_unwind(driver, products)
    print(f"Created {count} products")
    
    # Find similar
    similar = find_similar_products(driver, 'Laptop')
    for product, tags in similar:
        print(f"{product}: {tags}")
```

---

## Summary

### Key Concepts

1. **List Creation**: Literals, `range()`, `collect()`
2. **Access**: Index `[0]`, negative index `[-1]`, slicing `[1..3]`
3. **Comprehensions**: `[x IN list WHERE condition | transform]`
4. **UNWIND**: Convert list to rows for batch operations
5. **REDUCE**: Accumulate values across list elements
6. **Predicates**: `any()`, `all()`, `none()`, `single()`

### Quick Reference

```cypher
-- Create
[1, 2, 3], range(1, 10), collect(n.prop)

-- Access
list[0], list[-1], list[1..3], head(list), tail(list)

-- Transform
[x IN list | x * 2]
[x IN list WHERE x > 0 | x * 2]

-- Process
UNWIND list AS item
reduce(acc = 0, x IN list | acc + x)

-- Predicates
any(x IN list WHERE cond)
all(x IN list WHERE cond)

-- APOC
apoc.coll.sort(list)
apoc.coll.flatten(nested)
apoc.coll.union(a, b)
```

---

## Exercises

### Exercise 13.1: List Basics
1. Create a list of squared numbers from 1 to 10
2. Get every third element from a list
3. Reverse a list without using the reverse function

### Exercise 13.2: Comprehensions
1. Filter products over $100 and return their names uppercased
2. Create initials from a list of full names
3. Find common elements between two lists using comprehensions

### Exercise 13.3: UNWIND and REDUCE
1. Batch create nodes from a parameter list
2. Calculate factorial using REDUCE
3. Build a frequency map from a list of items

### Exercise 13.4: Advanced
1. Implement a moving average calculation
2. Group items into chunks of size N
3. Find the longest increasing subsequence in a list

---

**Next Chapter: [Chapter 14: Data Modeling Fundamentals](14-data-modeling-fundamentals.md)**
