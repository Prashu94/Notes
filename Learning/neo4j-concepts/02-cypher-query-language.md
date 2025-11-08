# Cypher Query Language - Complete Guide

## Table of Contents
1. [Introduction to Cypher](#introduction-to-cypher)
2. [Basic Syntax](#basic-syntax)
3. [CREATE - Creating Data](#create---creating-data)
4. [MATCH - Reading Data](#match---reading-data)
5. [WHERE - Filtering](#where---filtering)
6. [RETURN - Returning Results](#return---returning-results)
7. [UPDATE - Modifying Data](#update---modifying-data)
8. [DELETE - Removing Data](#delete---removing-data)
9. [Aggregations](#aggregations)
10. [Working with Relationships](#working-with-relationships)
11. [Pattern Matching](#pattern-matching)
12. [Advanced Queries](#advanced-queries)

---

## Introduction to Cypher

**Cypher** is Neo4j's declarative query language, designed specifically for working with graph data. It uses ASCII-art style syntax to represent patterns in graphs.

### Key Features
- **Declarative**: Describe WHAT you want, not HOW to get it
- **Pattern Matching**: Visual representation of graph patterns
- **SQL-inspired**: Familiar keywords (MATCH, WHERE, RETURN)
- **Expressive**: Complex queries in fewer lines

### Basic Pattern Syntax
```cypher
// Nodes are in parentheses
(n)              // Anonymous node
(p:Person)       // Node with label
(p:Person {name: "Alice"})  // Node with label and properties

// Relationships are in square brackets with arrows
-[r]->           // Directed relationship
-[r:KNOWS]->     // Typed relationship
<-[r:KNOWS]-     // Relationship in opposite direction
-[r:KNOWS*1..3]->  // Variable length path (1 to 3 hops)
```

---

## Basic Syntax

### Comments
```cypher
// Single-line comment

/* Multi-line
   comment */
```

### Case Sensitivity
- **Keywords**: Case-insensitive (MATCH = match = Match)
- **Labels**: Case-sensitive (Person ≠ person)
- **Property names**: Case-sensitive (name ≠ Name)
- **Relationship types**: Case-sensitive (KNOWS ≠ knows)

### Naming Conventions
- **Labels**: PascalCase (`:Person`, `:MovieGenre`)
- **Relationship Types**: SCREAMING_SNAKE_CASE (`:FRIENDS_WITH`, `:ACTED_IN`)
- **Properties**: camelCase (`firstName`, `createdAt`)

---

## CREATE - Creating Data

### Creating Nodes

#### Single Node
```cypher
// Create a simple node
CREATE (n)
RETURN n

// Create node with label
CREATE (p:Person)
RETURN p

// Create node with properties
CREATE (p:Person {
    name: "Alice Johnson",
    age: 30,
    email: "alice@example.com"
})
RETURN p

// Multiple labels
CREATE (u:Person:User:Employee {name: "Bob", employeeId: "E001"})
RETURN u
```

#### Multiple Nodes at Once
```cypher
CREATE 
    (alice:Person {name: "Alice", age: 30}),
    (bob:Person {name: "Bob", age: 35}),
    (charlie:Person {name: "Charlie", age: 28})
RETURN alice, bob, charlie
```

### Creating Relationships

#### With Existing Nodes
```cypher
// First, match the nodes
MATCH 
    (alice:Person {name: "Alice"}),
    (bob:Person {name: "Bob"})
// Then create relationship
CREATE (alice)-[r:FRIENDS_WITH {since: 2020}]->(bob)
RETURN alice, r, bob
```

#### Create Nodes and Relationships Together
```cypher
CREATE (alice:Person {name: "Alice"})-[r:WORKS_FOR {position: "Engineer"}]->(company:Company {name: "TechCorp"})
RETURN alice, r, company
```

#### Multiple Relationships
```cypher
CREATE 
    (alice:Person {name: "Alice"}),
    (bob:Person {name: "Bob"}),
    (charlie:Person {name: "Charlie"}),
    (alice)-[:FRIENDS_WITH]->(bob),
    (alice)-[:FRIENDS_WITH]->(charlie),
    (bob)-[:FRIENDS_WITH]->(charlie)
```

### MERGE - Create if Not Exists

MERGE is like CREATE but only creates if the pattern doesn't exist.

```cypher
// Create person only if doesn't exist
MERGE (p:Person {email: "alice@example.com"})
ON CREATE SET p.name = "Alice", p.createdAt = datetime()
ON MATCH SET p.lastSeen = datetime()
RETURN p
```

```cypher
// Create relationship only once
MATCH 
    (alice:Person {name: "Alice"}),
    (bob:Person {name: "Bob"})
MERGE (alice)-[r:FRIENDS_WITH]->(bob)
ON CREATE SET r.since = date()
RETURN alice, r, bob
```

---

## MATCH - Reading Data

### Basic Matching

#### Match All Nodes
```cypher
MATCH (n)
RETURN n
LIMIT 25
```

#### Match by Label
```cypher
MATCH (p:Person)
RETURN p
```

#### Match by Property
```cypher
MATCH (p:Person {name: "Alice"})
RETURN p
```

#### Match Multiple Labels
```cypher
MATCH (u:Person:Employee)
RETURN u
```

### Matching Relationships

#### Direct Relationships
```cypher
// Any relationship direction
MATCH (p:Person)-[r]-(other)
WHERE p.name = "Alice"
RETURN p, r, other

// Specific direction
MATCH (p:Person)-[r]->(other)
WHERE p.name = "Alice"
RETURN p, r, other

// Specific type
MATCH (p:Person)-[r:FRIENDS_WITH]->(friend:Person)
WHERE p.name = "Alice"
RETURN p, r, friend
```

#### Multiple Relationships
```cypher
// Chain of relationships
MATCH (p:Person)-[:WORKS_FOR]->(c:Company)<-[:WORKS_FOR]-(colleague:Person)
WHERE p.name = "Alice"
RETURN colleague.name AS Colleague, c.name AS Company
```

### Variable Length Paths

```cypher
// Friends of friends (exactly 2 hops)
MATCH (p:Person {name: "Alice"})-[:FRIENDS_WITH*2]-(fof:Person)
RETURN DISTINCT fof.name

// 1 to 3 hops
MATCH (p:Person {name: "Alice"})-[:FRIENDS_WITH*1..3]-(connection:Person)
RETURN DISTINCT connection.name

// Any depth (use carefully!)
MATCH (p:Person {name: "Alice"})-[:FRIENDS_WITH*]-(connection:Person)
RETURN DISTINCT connection.name
LIMIT 100
```

### Shortest Path

```cypher
// Find shortest path between two people
MATCH path = shortestPath(
    (alice:Person {name: "Alice"})-[:FRIENDS_WITH*]-(bob:Person {name: "Bob"})
)
RETURN path, length(path) AS pathLength

// All shortest paths
MATCH path = allShortestPaths(
    (alice:Person {name: "Alice"})-[:FRIENDS_WITH*]-(bob:Person {name: "Bob"})
)
RETURN path
```

---

## WHERE - Filtering

### Basic Comparisons

```cypher
MATCH (p:Person)
WHERE p.age > 25
RETURN p.name, p.age

// Multiple conditions with AND
MATCH (p:Person)
WHERE p.age > 25 AND p.age < 40
RETURN p.name, p.age

// OR conditions
MATCH (p:Person)
WHERE p.age < 25 OR p.age > 60
RETURN p.name, p.age

// NOT
MATCH (p:Person)
WHERE NOT p.age > 60
RETURN p.name, p.age
```

### String Matching

```cypher
// Exact match
MATCH (p:Person)
WHERE p.name = "Alice"
RETURN p

// STARTS WITH
MATCH (p:Person)
WHERE p.name STARTS WITH "A"
RETURN p.name

// ENDS WITH
MATCH (p:Person)
WHERE p.email ENDS WITH "@example.com"
RETURN p.name, p.email

// CONTAINS
MATCH (p:Person)
WHERE p.name CONTAINS "John"
RETURN p.name

// Case-insensitive with toLower()
MATCH (p:Person)
WHERE toLower(p.name) CONTAINS "alice"
RETURN p.name

// Regular expressions
MATCH (p:Person)
WHERE p.email =~ '.*@gmail\\.com$'
RETURN p.name, p.email
```

### NULL Checks

```cypher
// Check if property exists
MATCH (p:Person)
WHERE p.email IS NOT NULL
RETURN p.name, p.email

// Check if property doesn't exist
MATCH (p:Person)
WHERE p.middleName IS NULL
RETURN p.name
```

### List Operations

```cypher
// IN operator
MATCH (p:Person)
WHERE p.name IN ["Alice", "Bob", "Charlie"]
RETURN p.name

// Check if property is in a list
MATCH (p:Person)
WHERE p.age IN [25, 30, 35, 40]
RETURN p.name, p.age

// ALL - all elements must satisfy condition
MATCH (p:Person)
WHERE ALL(hobby IN p.hobbies WHERE hobby STARTS WITH "s")
RETURN p.name, p.hobbies

// ANY - at least one element satisfies
MATCH (p:Person)
WHERE ANY(hobby IN p.hobbies WHERE hobby = "reading")
RETURN p.name, p.hobbies

// NONE - no elements satisfy
MATCH (p:Person)
WHERE NONE(hobby IN p.hobbies WHERE hobby = "skydiving")
RETURN p.name
```

### Pattern Predicates

```cypher
// Node must have specific relationship
MATCH (p:Person)
WHERE (p)-[:WORKS_FOR]->(:Company {name: "TechCorp"})
RETURN p.name

// Node must NOT have relationship
MATCH (p:Person)
WHERE NOT (p)-[:WORKS_FOR]->()
RETURN p.name AS Unemployed

// Relationship with conditions
MATCH (p:Person)-[r:FRIENDS_WITH]->(friend)
WHERE r.since > date("2020-01-01")
RETURN p.name, friend.name, r.since
```

---

## RETURN - Returning Results

### Basic Returns

```cypher
// Return entire node
MATCH (p:Person)
RETURN p
LIMIT 10

// Return specific properties
MATCH (p:Person)
RETURN p.name, p.age

// Return with alias
MATCH (p:Person)
RETURN p.name AS Name, p.age AS Age

// Return relationships
MATCH (p:Person)-[r:FRIENDS_WITH]->(friend)
RETURN p.name, type(r) AS RelationshipType, friend.name
```

### DISTINCT

```cypher
// Return unique values only
MATCH (p:Person)-[:WORKS_FOR]->(c:Company)
RETURN DISTINCT c.name

// Distinct on multiple columns
MATCH (p:Person)
RETURN DISTINCT p.city, p.state
```

### ORDER BY

```cypher
// Ascending order (default)
MATCH (p:Person)
RETURN p.name, p.age
ORDER BY p.age

// Descending order
MATCH (p:Person)
RETURN p.name, p.age
ORDER BY p.age DESC

// Multiple columns
MATCH (p:Person)
RETURN p.name, p.city, p.age
ORDER BY p.city, p.age DESC

// Order by computed value
MATCH (p:Person)
RETURN p.name, p.age
ORDER BY p.age * 2 + 10 DESC
```

### LIMIT and SKIP

```cypher
// Limit results
MATCH (p:Person)
RETURN p.name
ORDER BY p.age
LIMIT 10

// Skip first N results (pagination)
MATCH (p:Person)
RETURN p.name, p.age
ORDER BY p.age
SKIP 20
LIMIT 10  // Get results 21-30

// Calculate total for pagination
MATCH (p:Person)
WITH count(p) AS total
MATCH (p:Person)
RETURN p.name, p.age, total
ORDER BY p.age
SKIP 0
LIMIT 10
```

### WITH - Pipeline Results

WITH allows you to chain query parts and process intermediate results.

```cypher
// Calculate average age, then find people above average
MATCH (p:Person)
WITH avg(p.age) AS avgAge
MATCH (p:Person)
WHERE p.age > avgAge
RETURN p.name, p.age, avgAge

// Find top 3 cities by person count, then find people in those cities
MATCH (p:Person)
WITH p.city, count(p) AS personCount
ORDER BY personCount DESC
LIMIT 3
MATCH (p:Person)
WHERE p.city IN collect(p.city)
RETURN p.name, p.city
```

---

## UPDATE - Modifying Data

### SET - Update Properties

```cypher
// Set single property
MATCH (p:Person {name: "Alice"})
SET p.age = 31
RETURN p

// Set multiple properties
MATCH (p:Person {name: "Alice"})
SET p.age = 31, p.city = "New York", p.updatedAt = datetime()
RETURN p

// Set property from another property
MATCH (p:Person {name: "Alice"})
SET p.displayName = p.name + " " + p.lastName
RETURN p

// Copy all properties from another node
MATCH (original:Person {name: "Alice"})
CREATE (copy:Person)
SET copy = original
RETURN copy

// Add properties without overwriting existing
MATCH (p:Person {name: "Alice"})
SET p += {phone: "555-1234", email: "alice@newdomain.com"}
RETURN p
```

### Add/Remove Labels

```cypher
// Add label
MATCH (p:Person {name: "Alice"})
SET p:Employee
RETURN p

// Add multiple labels
MATCH (p:Person {name: "Alice"})
SET p:Employee:Manager
RETURN p

// Remove label
MATCH (p:Person:Temporary)
REMOVE p:Temporary
RETURN p
```

### REMOVE - Delete Properties

```cypher
// Remove property
MATCH (p:Person {name: "Alice"})
REMOVE p.age
RETURN p

// Remove multiple properties
MATCH (p:Person {name: "Alice"})
REMOVE p.age, p.phone
RETURN p
```

---

## DELETE - Removing Data

### DELETE Nodes

```cypher
// Delete node (only works if no relationships)
MATCH (p:Person {name: "Alice"})
DELETE p

// DETACH DELETE removes node and all its relationships
MATCH (p:Person {name: "Alice"})
DETACH DELETE p

// Delete all nodes of a label (DANGEROUS!)
MATCH (t:TempNode)
DETACH DELETE t

// Delete all (VERY DANGEROUS!)
MATCH (n)
DETACH DELETE n
```

### DELETE Relationships

```cypher
// Delete specific relationship
MATCH (alice:Person {name: "Alice"})-[r:FRIENDS_WITH]->(bob:Person {name: "Bob"})
DELETE r

// Delete all relationships of a type
MATCH (p:Person)-[r:TEMPORARY_LINK]->()
DELETE r

// Delete relationships matching condition
MATCH (p:Person)-[r:FRIENDS_WITH]->()
WHERE r.since < date("2010-01-01")
DELETE r
```

---

## Aggregations

### COUNT

```cypher
// Count all nodes
MATCH (n)
RETURN count(n)

// Count by label
MATCH (p:Person)
RETURN count(p) AS totalPeople

// Count relationships
MATCH (p:Person)-[r:FRIENDS_WITH]->()
RETURN count(r) AS totalFriendships

// Count distinct
MATCH (p:Person)
RETURN count(DISTINCT p.city) AS uniqueCities

// Count with grouping
MATCH (p:Person)
RETURN p.city, count(p) AS peopleInCity
ORDER BY peopleInCity DESC
```

### SUM, AVG, MIN, MAX

```cypher
// Sum
MATCH (p:Person)
RETURN sum(p.age) AS totalAge

// Average
MATCH (p:Person)
RETURN avg(p.age) AS averageAge

// Min and Max
MATCH (p:Person)
RETURN min(p.age) AS youngest, max(p.age) AS oldest

// Multiple aggregations
MATCH (p:Person)
RETURN 
    count(p) AS total,
    avg(p.age) AS avgAge,
    min(p.age) AS minAge,
    max(p.age) AS maxAge,
    sum(p.age) AS sumAge
```

### COLLECT

```cypher
// Collect into list
MATCH (p:Person)
RETURN collect(p.name) AS allNames

// Collect with limit
MATCH (p:Person)
RETURN collect(p.name)[0..5] AS first5Names

// Collect related nodes
MATCH (company:Company)<-[:WORKS_FOR]-(employee:Person)
RETURN company.name, collect(employee.name) AS employees

// Collect distinct
MATCH (p:Person)
RETURN collect(DISTINCT p.city) AS uniqueCities
```

---

## Working with Relationships

### Relationship Direction

```cypher
// Outgoing relationships
MATCH (p:Person)-[r:FRIENDS_WITH]->(friend)
WHERE p.name = "Alice"
RETURN friend.name

// Incoming relationships
MATCH (p:Person)<-[r:FOLLOWS]-(follower)
WHERE p.name = "Alice"
RETURN follower.name AS Followers

// Any direction (bidirectional)
MATCH (p:Person)-[r:FRIENDS_WITH]-(friend)
WHERE p.name = "Alice"
RETURN friend.name
```

### Relationship Properties

```cypher
// Filter by relationship properties
MATCH (p:Person)-[r:FRIENDS_WITH]->(friend)
WHERE p.name = "Alice" AND r.since > date("2020-01-01")
RETURN friend.name, r.since

// Update relationship properties
MATCH (p:Person)-[r:FRIENDS_WITH]->(friend)
WHERE p.name = "Alice" AND friend.name = "Bob"
SET r.closeness = "best friends", r.updatedAt = datetime()
RETURN r

// Return relationship properties
MATCH (p:Person)-[r:FRIENDS_WITH]->(friend)
WHERE p.name = "Alice"
RETURN friend.name, r.since, r.closeness
```

### Multiple Relationship Types

```cypher
// Match multiple types with OR (|)
MATCH (p:Person)-[r:FRIENDS_WITH|FOLLOWS]->(other)
WHERE p.name = "Alice"
RETURN other.name, type(r) AS relationshipType

// Different relationships to same node
MATCH (alice:Person {name: "Alice"}),
      (bob:Person {name: "Bob"})
CREATE (alice)-[:FRIENDS_WITH]->(bob),
       (alice)-[:FOLLOWS]->(bob),
       (alice)-[:WORKS_WITH]->(bob)
```

---

## Pattern Matching

### Complex Patterns

```cypher
// Triangle pattern (mutual friends)
MATCH (a:Person)-[:FRIENDS_WITH]->(b:Person)-[:FRIENDS_WITH]->(c:Person),
      (a)-[:FRIENDS_WITH]->(c)
RETURN a.name, b.name, c.name

// Find common friends
MATCH (alice:Person {name: "Alice"})-[:FRIENDS_WITH]->(friend)<-[:FRIENDS_WITH]-(bob:Person {name: "Bob"})
RETURN friend.name AS CommonFriend

// People who work at the same company
MATCH (p1:Person)-[:WORKS_FOR]->(c:Company)<-[:WORKS_FOR]-(p2:Person)
WHERE p1.name = "Alice" AND p1 <> p2
RETURN p2.name AS Colleague, c.name AS Company
```

### Optional Patterns

OPTIONAL MATCH is like LEFT JOIN in SQL.

```cypher
// Return people and their companies (include people without companies)
MATCH (p:Person)
OPTIONAL MATCH (p)-[:WORKS_FOR]->(c:Company)
RETURN p.name, c.name AS company

// Multiple optional matches
MATCH (p:Person)
OPTIONAL MATCH (p)-[:WORKS_FOR]->(c:Company)
OPTIONAL MATCH (p)-[r:FRIENDS_WITH]->(friend:Person)
RETURN p.name, c.name AS company, collect(friend.name) AS friends
```

### UNION

```cypher
// Combine results from multiple queries
MATCH (p:Person {city: "San Francisco"})
RETURN p.name AS name, "San Francisco" AS location
UNION
MATCH (p:Person {city: "New York"})
RETURN p.name AS name, "New York" AS location

// UNION ALL (includes duplicates)
MATCH (p:Person)-[:WORKS_FOR]->(c:Company)
RETURN p.name AS name
UNION ALL
MATCH (p:Person)-[:FRIENDS_WITH]->(friend:Person)
RETURN friend.name AS name
```

---

## Advanced Queries

### CASE Expressions

```cypher
// Simple CASE
MATCH (p:Person)
RETURN p.name,
CASE p.age
    WHEN 25 THEN "Quarter century"
    WHEN 50 THEN "Half century"
    ELSE "Other age"
END AS ageCategory

// Generic CASE
MATCH (p:Person)
RETURN p.name, p.age,
CASE
    WHEN p.age < 18 THEN "Minor"
    WHEN p.age < 65 THEN "Adult"
    ELSE "Senior"
END AS ageGroup
```

### List Comprehensions

```cypher
// Transform list elements
MATCH (p:Person)
WHERE p.hobbies IS NOT NULL
RETURN p.name, [hobby IN p.hobbies | toUpper(hobby)] AS uppercaseHobbies

// Filter list elements
MATCH (p:Person)
WHERE p.hobbies IS NOT NULL
RETURN p.name, [hobby IN p.hobbies WHERE hobby STARTS WITH "s"] AS sHobbies

// Extract and transform
MATCH (p:Person)-[:HAS_SKILL]->(s:Skill)
WITH p, collect(s.name) AS skills
RETURN p.name, [skill IN skills WHERE skill CONTAINS "Python"] AS pythonSkills
```

### UNWIND - List to Rows

```cypher
// Convert list to rows
UNWIND ["Alice", "Bob", "Charlie"] AS name
CREATE (p:Person {name: name})
RETURN p

// Unwind with existing data
MATCH (p:Person {name: "Alice"})
UNWIND p.hobbies AS hobby
RETURN p.name, hobby

// Multiple unwinds (cartesian product)
UNWIND ["Alice", "Bob"] AS name
UNWIND ["Reading", "Hiking"] AS hobby
CREATE (p:Person {name: name, hobby: hobby})
```

### EXISTS - Subqueries

```cypher
// Check if pattern exists (Neo4j 4.x+)
MATCH (p:Person)
WHERE EXISTS {
    MATCH (p)-[:WORKS_FOR]->(:Company {name: "TechCorp"})
}
RETURN p.name

// Negative existence
MATCH (p:Person)
WHERE NOT EXISTS {
    MATCH (p)-[:FRIENDS_WITH]->()
}
RETURN p.name AS loners
```

### CALL - Procedures

```cypher
// Call built-in procedure
CALL db.labels()
YIELD label
RETURN label

// Call with arguments
CALL db.index.fulltext.queryNodes("personIndex", "Alice")
YIELD node, score
RETURN node.name, score

// APOC procedures (if installed)
CALL apoc.meta.graph()
YIELD nodes, relationships
RETURN nodes, relationships
```

### Performance: EXPLAIN and PROFILE

```cypher
// Show query plan without executing
EXPLAIN
MATCH (p:Person {name: "Alice"})-[:FRIENDS_WITH]->(friend)
RETURN friend.name

// Execute and show performance metrics
PROFILE
MATCH (p:Person {name: "Alice"})-[:FRIENDS_WITH]->(friend)
RETURN friend.name
```

---

## Common Query Patterns

### Pagination

```cypher
// Page 1 (results 0-9)
MATCH (p:Person)
RETURN p.name
ORDER BY p.name
SKIP 0 LIMIT 10

// Page 2 (results 10-19)
MATCH (p:Person)
RETURN p.name
ORDER BY p.name
SKIP 10 LIMIT 10
```

### Recommendations

```cypher
// Friend of friend recommendations (exclude existing friends)
MATCH (me:Person {name: "Alice"})-[:FRIENDS_WITH]->()-[:FRIENDS_WITH]->(recommendation:Person)
WHERE NOT (me)-[:FRIENDS_WITH]->(recommendation) AND me <> recommendation
RETURN recommendation.name, count(*) AS mutualFriends
ORDER BY mutualFriends DESC
LIMIT 10
```

### Find Influencers

```cypher
// People with most followers
MATCH (p:Person)<-[r:FOLLOWS]-()
RETURN p.name, count(r) AS followers
ORDER BY followers DESC
LIMIT 10
```

### Degree Centrality

```cypher
// Count connections
MATCH (p:Person)-[r]-()
RETURN p.name, count(r) AS connections
ORDER BY connections DESC
LIMIT 10
```

---

## Quick Reference

### Clause Order
```cypher
MATCH     // Find patterns
WHERE     // Filter results
WITH      // Pass results to next part
RETURN    // Output results
ORDER BY  // Sort
SKIP      // Skip results
LIMIT     // Limit results
```

### Essential Functions

```cypher
// String functions
toUpper(), toLower(), trim(), substring(), split()

// Math functions
abs(), ceil(), floor(), round(), sqrt(), rand()

// Aggregation
count(), sum(), avg(), min(), max(), collect()

// List functions
size(), head(), tail(), last(), reverse()

// Node/Relationship functions
id(), labels(), type(), properties(), keys()

// Temporal
date(), datetime(), timestamp(), duration()
```

---

**Next:** Proceed to [03-advanced-concepts.md](03-advanced-concepts.md) for indexes, constraints, and performance optimization.
