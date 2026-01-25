# Chapter 4: Cypher Fundamentals

## Learning Objectives
By the end of this chapter, you will:
- Understand Cypher's design philosophy and syntax
- Know the basic structure of Cypher queries
- Understand pattern matching concepts
- Work with variables and parameters
- Handle basic expressions and operators

---

## 4.1 What is Cypher?

### Overview

**Cypher** is Neo4j's declarative query language, designed specifically for graph databases.

| Feature | Description |
|---------|-------------|
| **Declarative** | You describe WHAT you want, not HOW to get it |
| **Pattern-based** | Queries match visual graph patterns |
| **SQL-influenced** | Familiar keywords for SQL users |
| **ASCII-art syntax** | Patterns look like the graph structure |

### Cypher vs SQL Comparison

```
SQL (Relational):
─────────────────
SELECT p.name, c.name
FROM persons p
JOIN employed_at e ON p.id = e.person_id
JOIN companies c ON e.company_id = c.id
WHERE c.name = 'TechCorp'

Cypher (Graph):
───────────────
MATCH (p:Person)-[:WORKS_FOR]->(c:Company {name: 'TechCorp'})
RETURN p.name, c.name
```

### Visual Pattern Syntax

Cypher patterns mirror ASCII art representations of graphs:

```
Node:           ()
Named node:     (n)
Labeled node:   (n:Person)
With props:     (n:Person {name: 'Alice'})

Relationship:   -[]-
Named:          -[r]-
Typed:          -[r:KNOWS]-
Directed:       -[r:KNOWS]->
With props:     -[r:KNOWS {since: 2020}]->
```

---

## 4.2 Basic Query Structure

### Query Anatomy

```cypher
MATCH pattern           // Find data matching pattern
WHERE condition         // Filter results
RETURN expression       // Return results
ORDER BY expression     // Sort results
SKIP n                  // Skip first n rows
LIMIT n                 // Return only n rows
```

### Simple Query Examples

```cypher
// Find all Person nodes
MATCH (p:Person)
RETURN p

// Find person named Alice
MATCH (p:Person {name: 'Alice'})
RETURN p

// Find with WHERE clause
MATCH (p:Person)
WHERE p.name = 'Alice'
RETURN p

// Return specific properties
MATCH (p:Person {name: 'Alice'})
RETURN p.name, p.age

// With alias
MATCH (p:Person {name: 'Alice'})
RETURN p.name AS personName, p.age AS personAge
```

### Complete Query Example

```cypher
// Full query structure
MATCH (p:Person)-[:WORKS_FOR]->(c:Company)
WHERE p.age > 25 AND c.industry = 'Technology'
RETURN p.name AS employee, c.name AS company, p.age
ORDER BY p.age DESC
SKIP 5
LIMIT 10
```

---

## 4.3 Pattern Matching Deep Dive

### Node Patterns

```cypher
// Any node
MATCH (n)
RETURN n LIMIT 5

// Node with specific label
MATCH (p:Person)
RETURN p

// Node with multiple labels
MATCH (p:Person:Employee)
RETURN p

// Node with property inline
MATCH (p:Person {name: 'Alice'})
RETURN p

// Node with multiple properties
MATCH (p:Person {name: 'Alice', age: 30})
RETURN p
```

### Relationship Patterns

```cypher
// Any relationship (any direction)
MATCH (a)-[r]-(b)
RETURN a, r, b LIMIT 5

// Outgoing relationship
MATCH (a)-[r]->(b)
RETURN a, r, b LIMIT 5

// Incoming relationship
MATCH (a)<-[r]-(b)
RETURN a, r, b LIMIT 5

// Specific relationship type
MATCH (p:Person)-[r:KNOWS]->(other:Person)
RETURN p.name, other.name

// Multiple relationship types (OR)
MATCH (p:Person)-[r:KNOWS|FRIENDS_WITH]->(other)
RETURN p.name, type(r), other.name

// Relationship with properties
MATCH (p:Person)-[r:KNOWS {since: 2020}]->(other)
RETURN p.name, other.name
```

### Path Patterns

```cypher
// Chain of relationships
MATCH (a:Person)-[:KNOWS]->(b:Person)-[:WORKS_FOR]->(c:Company)
RETURN a.name, b.name, c.name

// Variable length paths
// Exactly 2 hops
MATCH (a:Person)-[:KNOWS*2]->(b:Person)
RETURN a.name, b.name

// 1 to 3 hops
MATCH (a:Person)-[:KNOWS*1..3]->(b:Person)
RETURN a.name, b.name

// 2 or more hops
MATCH (a:Person)-[:KNOWS*2..]->(b:Person)
RETURN a.name, b.name

// Any number of hops (be careful with large graphs!)
MATCH (a:Person)-[:KNOWS*]->(b:Person)
RETURN a.name, b.name
```

### Named Paths

```cypher
// Assign path to variable
MATCH path = (a:Person {name: 'Alice'})-[:KNOWS*]-(b:Person {name: 'Charlie'})
RETURN path

// Extract from path
MATCH path = (a:Person)-[:KNOWS*1..3]-(b:Person)
WHERE a.name = 'Alice'
RETURN path,
       length(path) AS pathLength,
       nodes(path) AS nodesInPath,
       relationships(path) AS relsInPath
```

---

## 4.4 Variables and Binding

### Variable Naming Rules

```
✅ Valid variable names:
   n, node, person, p1, myVariable, _temp

❌ Invalid variable names:
   123var (can't start with number)
   my-var (no hyphens)
   my var (no spaces)
```

### Variable Scope

```cypher
// Variables are scoped to the query
MATCH (p:Person {name: 'Alice'})  // p is bound here
WHERE p.age > 25                   // p is accessible
RETURN p.name                      // p is accessible

// Variables must be bound before use
MATCH (p:Person)
WHERE p.age > 25
RETURN p.name, q.name  // ERROR: q is not defined!

// Multiple bindings in same MATCH
MATCH (p:Person)-[r:KNOWS]->(f:Person)
// p, r, and f are all accessible
RETURN p.name, r.since, f.name
```

### Reusing Variables

```cypher
// Same variable can be used in multiple patterns
MATCH (p:Person {name: 'Alice'})-[:KNOWS]->(f:Person)
MATCH (p)-[:WORKS_FOR]->(c:Company)
// p refers to the same Alice node in both patterns
RETURN p.name, f.name, c.name
```

---

## 4.5 Parameters

### Why Use Parameters?

1. **Security**: Prevent Cypher injection
2. **Performance**: Enable query plan caching
3. **Reusability**: Same query with different values

### Setting Parameters in Neo4j Browser

```cypher
// Set a single parameter
:param name => 'Alice'

// Set multiple parameters
:params {name: 'Alice', minAge: 25}

// View current parameters
:params

// Clear all parameters
:params {}
```

### Using Parameters in Queries

```cypher
// With parameter set as: :param name => 'Alice'
MATCH (p:Person {name: $name})
RETURN p

// Multiple parameters
// :params {minAge: 25, company: 'TechCorp'}
MATCH (p:Person)-[:WORKS_FOR]->(c:Company {name: $company})
WHERE p.age >= $minAge
RETURN p.name

// Parameters in relationships
// :param since => 2020
MATCH (a)-[:KNOWS {since: $since}]->(b)
RETURN a.name, b.name
```

### Parameters in Python

```python
from neo4j import GraphDatabase

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))

with driver.session() as session:
    # Parameters as a dictionary
    result = session.run(
        "MATCH (p:Person {name: $name}) RETURN p.age AS age",
        name="Alice"  # Parameters as keyword arguments
    )
    
    # Or using a dict
    params = {"name": "Alice", "minAge": 25}
    result = session.run(
        """
        MATCH (p:Person)
        WHERE p.name = $name AND p.age >= $minAge
        RETURN p
        """,
        parameters=params
    )
```

---

## 4.6 Expressions and Operators

### Arithmetic Operators

```cypher
// Basic arithmetic
RETURN 10 + 5 AS addition      // 15
RETURN 10 - 5 AS subtraction   // 5
RETURN 10 * 5 AS multiplication // 50
RETURN 10 / 3 AS division      // 3 (integer division)
RETURN 10.0 / 3 AS floatDiv    // 3.333...
RETURN 10 % 3 AS modulo        // 1
RETURN 2 ^ 10 AS power         // 1024

// In queries
MATCH (p:Product)
RETURN p.name, p.price * 1.1 AS priceWithTax
```

### Comparison Operators

```cypher
// Equals
MATCH (p:Person) WHERE p.age = 30 RETURN p

// Not equals
MATCH (p:Person) WHERE p.age <> 30 RETURN p

// Less than / greater than
MATCH (p:Person) WHERE p.age < 30 RETURN p
MATCH (p:Person) WHERE p.age > 30 RETURN p
MATCH (p:Person) WHERE p.age <= 30 RETURN p
MATCH (p:Person) WHERE p.age >= 30 RETURN p

// Comparison with NULL
MATCH (p:Person) WHERE p.email IS NULL RETURN p
MATCH (p:Person) WHERE p.email IS NOT NULL RETURN p
```

### Boolean Operators

```cypher
// AND
MATCH (p:Person)
WHERE p.age > 25 AND p.city = 'NYC'
RETURN p

// OR
MATCH (p:Person)
WHERE p.city = 'NYC' OR p.city = 'LA'
RETURN p

// NOT
MATCH (p:Person)
WHERE NOT p.age > 30
RETURN p

// XOR (exclusive or)
MATCH (p:Person)
WHERE p.isManager XOR p.isDeveloper
RETURN p

// Combined
MATCH (p:Person)
WHERE (p.age > 25 AND p.city = 'NYC') OR p.isVIP
RETURN p
```

### String Operators

```cypher
// Concatenation
RETURN 'Hello' + ' ' + 'World' AS greeting

// STARTS WITH
MATCH (p:Person)
WHERE p.name STARTS WITH 'Al'
RETURN p.name

// ENDS WITH
MATCH (p:Person)
WHERE p.email ENDS WITH '@gmail.com'
RETURN p.name

// CONTAINS
MATCH (p:Person)
WHERE p.bio CONTAINS 'engineer'
RETURN p.name

// Regular expression
MATCH (p:Person)
WHERE p.name =~ 'A.*'  // Names starting with A
RETURN p.name

// Case-insensitive regex
MATCH (p:Person)
WHERE p.name =~ '(?i)alice'
RETURN p.name
```

### List Operators

```cypher
// IN operator
MATCH (p:Person)
WHERE p.city IN ['NYC', 'LA', 'Chicago']
RETURN p.name

// List concatenation
RETURN [1, 2] + [3, 4] AS combined  // [1, 2, 3, 4]

// List access
WITH ['a', 'b', 'c', 'd'] AS letters
RETURN letters[0] AS first,      // 'a'
       letters[-1] AS last,      // 'd'
       letters[1..3] AS slice    // ['b', 'c']
```

---

## 4.7 Comments

### Single-line Comments

```cypher
// This is a single-line comment
MATCH (p:Person)  // Find all persons
RETURN p.name
```

### Multi-line Comments

```cypher
/* 
 * This is a multi-line comment
 * It can span multiple lines
 * Useful for documentation
 */
MATCH (p:Person)
WHERE p.age > 25
RETURN p.name
```

### Practical Documentation

```cypher
/*
 * Query: Find employees eligible for promotion
 * Author: John Doe
 * Date: 2024-01-15
 * 
 * Business Rule: 
 *   - At least 2 years with company
 *   - Performance rating >= 4
 *   - No active disciplinary actions
 */
MATCH (e:Employee)-[:WORKS_FOR]->(c:Company)
WHERE e.startDate < date() - duration('P2Y')  // 2+ years
  AND e.performanceRating >= 4
  AND NOT e:UnderReview
RETURN e.name, e.department
ORDER BY e.performanceRating DESC
```

---

## 4.8 NULL Handling

### Understanding NULL

In Cypher, `NULL` represents:
- Missing or unknown values
- Properties that don't exist
- Failed comparisons

### NULL in Comparisons

```cypher
// NULL comparisons always return NULL (not true/false)
RETURN null = null      // null (not true!)
RETURN null <> null     // null
RETURN null AND true    // null
RETURN null OR true     // true (short-circuit)
RETURN null OR false    // null

// Checking for NULL
RETURN null IS NULL     // true
RETURN null IS NOT NULL // false
RETURN 'value' IS NULL  // false
```

### NULL in Queries

```cypher
// Find nodes where property is null
MATCH (p:Person)
WHERE p.email IS NULL
RETURN p.name

// Find nodes where property exists
MATCH (p:Person)
WHERE p.email IS NOT NULL
RETURN p.name, p.email

// COALESCE: return first non-null value
MATCH (p:Person)
RETURN p.name, 
       coalesce(p.nickname, p.name) AS displayName

// Handle potential nulls in calculations
MATCH (p:Product)
RETURN p.name,
       coalesce(p.discount, 0) AS discount,
       p.price * (1 - coalesce(p.discount, 0)) AS finalPrice
```

### NULL in Aggregations

```cypher
// NULL values are generally ignored in aggregations
MATCH (p:Person)
RETURN count(p) AS total,           // Counts all persons
       count(p.email) AS withEmail  // Counts only non-null emails
```

---

## 4.9 CASE Expressions

### Simple CASE

```cypher
// Matching specific values
MATCH (p:Person)
RETURN p.name,
       CASE p.status
         WHEN 'A' THEN 'Active'
         WHEN 'I' THEN 'Inactive'
         WHEN 'P' THEN 'Pending'
         ELSE 'Unknown'
       END AS statusText
```

### Generic CASE

```cypher
// Matching conditions
MATCH (p:Person)
RETURN p.name, p.age,
       CASE
         WHEN p.age < 18 THEN 'Minor'
         WHEN p.age < 65 THEN 'Adult'
         ELSE 'Senior'
       END AS ageGroup
```

### Practical CASE Examples

```cypher
// Categorize products by price
MATCH (p:Product)
RETURN p.name, p.price,
       CASE
         WHEN p.price < 10 THEN 'Budget'
         WHEN p.price < 50 THEN 'Mid-range'
         WHEN p.price < 100 THEN 'Premium'
         ELSE 'Luxury'
       END AS priceCategory

// Dynamic relationship description
MATCH (a:Person)-[r]->(b)
RETURN a.name,
       CASE type(r)
         WHEN 'KNOWS' THEN 'is acquainted with'
         WHEN 'FRIENDS_WITH' THEN 'is friends with'
         WHEN 'WORKS_FOR' THEN 'works for'
         ELSE 'is connected to'
       END AS relationship,
       b.name
```

---

## 4.10 Type Checking and Conversion

### Check Types

```cypher
// Check value type
RETURN valueType(42)           // "INTEGER"
RETURN valueType(3.14)         // "FLOAT"
RETURN valueType('hello')      // "STRING"
RETURN valueType(true)         // "BOOLEAN"
RETURN valueType([1,2,3])      // "LIST<INTEGER>"
RETURN valueType(null)         // "NULL"
```

### Type Conversion Functions

```cypher
// To String
RETURN toString(123)           // "123"
RETURN toString(3.14)          // "3.14"
RETURN toString(true)          // "true"

// To Integer
RETURN toInteger('42')         // 42
RETURN toInteger(3.7)          // 3 (truncates)
RETURN toInteger(true)         // 1
RETURN toInteger(false)        // 0

// To Float
RETURN toFloat('3.14')         // 3.14
RETURN toFloat(42)             // 42.0

// To Boolean
RETURN toBoolean('true')       // true
RETURN toBoolean('false')      // false
RETURN toBoolean(1)            // true
RETURN toBoolean(0)            // false

// Safe conversions (return null on failure)
RETURN toIntegerOrNull('abc')  // null
RETURN toFloatOrNull('xyz')    // null
```

### Type Predicates

```cypher
// Check if value is of specific type
RETURN 42 IS :: INTEGER        // true
RETURN 'hello' IS :: STRING    // true
RETURN [1,2,3] IS :: LIST<INTEGER>  // true

// In WHERE clause
MATCH (n)
WHERE n.value IS :: INTEGER
RETURN n
```

---

## 4.11 Query Execution Order

Understanding the order of clause execution:

```
┌─────────────────────────────────────────────────────────────┐
│              CYPHER QUERY EXECUTION ORDER                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. MATCH        ─── Find patterns in the graph            │
│         ↓                                                   │
│  2. WHERE        ─── Filter based on conditions            │
│         ↓                                                   │
│  3. WITH         ─── Project/aggregate intermediate results│
│         ↓                                                   │
│  4. ORDER BY     ─── Sort results                          │
│         ↓                                                   │
│  5. SKIP         ─── Skip first N rows                     │
│         ↓                                                   │
│  6. LIMIT        ─── Take only N rows                      │
│         ↓                                                   │
│  7. RETURN       ─── Output final results                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Execution Order Examples

```cypher
// Order matters!
MATCH (p:Person)         // 1. Find all Person nodes
WHERE p.age > 25         // 2. Keep only those > 25
WITH p                   // 3. Pass through
ORDER BY p.age DESC      // 4. Sort by age descending
SKIP 10                  // 5. Skip first 10
LIMIT 5                  // 6. Take next 5
RETURN p.name, p.age     // 7. Return name and age
```

---

## 4.12 Common Query Patterns

### Pattern 1: Simple Lookup

```cypher
// Find by property
MATCH (p:Person {name: 'Alice'})
RETURN p

// Find by multiple criteria
MATCH (p:Person)
WHERE p.age > 25 AND p.city = 'NYC'
RETURN p.name, p.age
```

### Pattern 2: Traverse Relationships

```cypher
// One hop
MATCH (p:Person)-[:WORKS_FOR]->(c:Company)
RETURN p.name, c.name

// Multiple hops
MATCH (p:Person)-[:KNOWS]->(:Person)-[:KNOWS]->(fof:Person)
WHERE p.name = 'Alice' AND fof <> p
RETURN DISTINCT fof.name AS friendOfFriend
```

### Pattern 3: Find Connections

```cypher
// Find if two nodes are connected
MATCH (a:Person {name: 'Alice'}), (b:Person {name: 'Bob'})
MATCH path = shortestPath((a)-[*]-(b))
RETURN path
```

### Pattern 4: Count and Aggregate

```cypher
// Count by category
MATCH (p:Person)-[:LIVES_IN]->(c:City)
RETURN c.name, count(p) AS residents
ORDER BY residents DESC
```

### Pattern 5: Conditional Creation

```cypher
// Create only if not exists (MERGE)
MERGE (p:Person {name: 'Alice'})
ON CREATE SET p.created = datetime()
ON MATCH SET p.lastSeen = datetime()
RETURN p
```

---

## Summary

### Key Takeaways

1. **Cypher is declarative**: Describe what you want, not how
2. **Pattern-based syntax**: Visual ASCII-art patterns
3. **Variables bind to graph elements**: Nodes and relationships
4. **Parameters improve security and performance**
5. **NULL requires special handling**: Use IS NULL/IS NOT NULL
6. **Execution order matters**: MATCH → WHERE → WITH → ORDER → SKIP → LIMIT → RETURN

### Cypher Quick Reference

```
PATTERN MATCHING:
  (n)                 - Any node
  (n:Label)           - Labeled node
  (n {prop: val})     - Node with property
  -[r]->              - Relationship
  -[r:TYPE]->         - Typed relationship
  -[*1..3]->          - Variable length (1-3 hops)

CLAUSES:
  MATCH               - Find patterns
  WHERE               - Filter results
  RETURN              - Output results
  ORDER BY            - Sort results
  SKIP/LIMIT          - Paginate results
  WITH                - Chain queries

OPERATORS:
  =, <>, <, >, <=, >= - Comparison
  AND, OR, NOT, XOR   - Boolean
  +, -, *, /, %, ^    - Arithmetic
  IN, STARTS WITH,    - String/List
  ENDS WITH, CONTAINS
```

---

## Exercises

### Exercise 4.1: Basic Patterns
Write queries to:
1. Find all nodes in the database
2. Find all Person nodes
3. Find all relationships in the database
4. Find all KNOWS relationships

### Exercise 4.2: Property Filtering
Write queries to find:
1. People older than 30
2. Products priced between $10 and $50
3. People whose name starts with 'A'
4. Orders from 2024

### Exercise 4.3: Relationship Patterns
Write queries to:
1. Find all people who know Alice
2. Find all people Alice knows
3. Find friends of friends
4. Find the shortest path between two people

### Exercise 4.4: Parameterized Queries
Create parameterized queries for:
1. Finding a person by name
2. Finding products in a price range
3. Finding people in a specific city
4. Finding relationships created after a certain date

### Exercise 4.5: NULL Handling
Write queries that:
1. Find people without email addresses
2. Return a default value when a property is missing
3. Count how many people have each optional property

---

**Next Chapter: [Chapter 5: Cypher - Reading Data](05-cypher-reading-data.md)**
