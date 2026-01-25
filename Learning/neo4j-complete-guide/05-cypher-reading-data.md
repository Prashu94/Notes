# Chapter 5: Cypher - Reading Data (MATCH, WHERE, RETURN)

## Learning Objectives
By the end of this chapter, you will:
- Master the MATCH clause for pattern matching
- Use WHERE for complex filtering
- Control output with RETURN
- Understand OPTIONAL MATCH for null-safe matching
- Work with aliases and expressions in results

---

## 5.1 The MATCH Clause

### Purpose

`MATCH` finds patterns in the graph. It's the primary way to read data.

### Basic Syntax

```cypher
MATCH pattern
[WHERE condition]
RETURN expression
```

### Matching Nodes

```cypher
// Match all nodes
MATCH (n)
RETURN n
LIMIT 10

// Match nodes with specific label
MATCH (p:Person)
RETURN p

// Match nodes with property
MATCH (p:Person {name: 'Alice'})
RETURN p

// Match nodes with multiple labels
MATCH (n:Person:Developer)
RETURN n

// Match nodes with multiple properties
MATCH (p:Person {name: 'Alice', city: 'NYC'})
RETURN p
```

### Matching Relationships

```cypher
// Match any relationship
MATCH (a)-[r]->(b)
RETURN a, r, b
LIMIT 5

// Match specific relationship type
MATCH (p:Person)-[r:KNOWS]->(other:Person)
RETURN p.name, other.name

// Match without caring about direction
MATCH (p:Person)-[r:KNOWS]-(other:Person)
RETURN p.name, other.name

// Match multiple relationship types
MATCH (p:Person)-[r:KNOWS|FRIENDS_WITH]->(other)
RETURN p.name, type(r), other.name

// Match relationship with properties
MATCH (p:Person)-[r:KNOWS {since: 2020}]->(other)
RETURN p.name, other.name
```

### Matching Paths

```cypher
// Match a path and bind to variable
MATCH path = (a:Person)-[:KNOWS]->(b:Person)
RETURN path

// Match longer paths
MATCH path = (a:Person)-[:KNOWS]->(b)-[:KNOWS]->(c)
RETURN path, nodes(path), relationships(path)

// Variable-length paths
MATCH path = (a:Person {name: 'Alice'})-[:KNOWS*1..3]->(b:Person)
RETURN path, length(path) AS hops
```

### Multiple MATCH Clauses

```cypher
// Multiple patterns in same MATCH (Cartesian product if unconnected!)
MATCH (p:Person {name: 'Alice'}), (c:Company {name: 'TechCorp'})
RETURN p, c

// Connected patterns
MATCH (p:Person)-[:KNOWS]->(friend:Person),
      (friend)-[:WORKS_FOR]->(company:Company)
RETURN p.name, friend.name, company.name

// Sequential MATCH clauses
MATCH (p:Person {name: 'Alice'})
MATCH (p)-[:KNOWS]->(friend)
MATCH (friend)-[:WORKS_FOR]->(company)
RETURN p.name, friend.name, company.name
```

---

## 5.2 The WHERE Clause

### Purpose

`WHERE` filters results based on conditions. It works with MATCH, OPTIONAL MATCH, and WITH.

### Basic Comparisons

```cypher
// Equality
MATCH (p:Person)
WHERE p.name = 'Alice'
RETURN p

// Not equal
MATCH (p:Person)
WHERE p.city <> 'NYC'
RETURN p.name

// Numeric comparisons
MATCH (p:Person)
WHERE p.age > 25
RETURN p.name, p.age

MATCH (p:Person)
WHERE p.age >= 25 AND p.age <= 35
RETURN p.name, p.age

// BETWEEN alternative
MATCH (p:Person)
WHERE 25 <= p.age <= 35
RETURN p.name, p.age
```

### Boolean Logic

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
WHERE NOT p.city = 'NYC'
RETURN p

// Complex combinations
MATCH (p:Person)
WHERE (p.age > 25 AND p.city = 'NYC') 
   OR (p.age > 30 AND p.isVIP = true)
RETURN p

// XOR
MATCH (p:Person)
WHERE p.isManager XOR p.isDeveloper  // one but not both
RETURN p
```

### String Matching

```cypher
// Exact match
MATCH (p:Person)
WHERE p.name = 'Alice'
RETURN p

// STARTS WITH
MATCH (p:Person)
WHERE p.name STARTS WITH 'Al'
RETURN p.name

// ENDS WITH
MATCH (p:Person)
WHERE p.email ENDS WITH '@gmail.com'
RETURN p.name, p.email

// CONTAINS
MATCH (p:Person)
WHERE p.bio CONTAINS 'engineer'
RETURN p.name

// Regular expressions
MATCH (p:Person)
WHERE p.name =~ 'A.*'  // Names starting with A
RETURN p.name

// Case-insensitive regex
MATCH (p:Person)
WHERE p.name =~ '(?i)alice'  // any case of 'alice'
RETURN p.name

// Complex regex
MATCH (p:Person)
WHERE p.email =~ '.*@(gmail|yahoo)\\.com'
RETURN p.name, p.email
```

### List Operations

```cypher
// IN operator
MATCH (p:Person)
WHERE p.city IN ['NYC', 'LA', 'Chicago']
RETURN p.name, p.city

// NOT IN
MATCH (p:Person)
WHERE NOT p.city IN ['NYC', 'LA']
RETURN p.name

// Check list property
MATCH (m:Movie)
WHERE 'Action' IN m.genres
RETURN m.title

// All elements match
MATCH (p:Person)
WHERE all(skill IN p.skills WHERE skill STARTS WITH 'Java')
RETURN p.name

// Any element matches
MATCH (p:Person)
WHERE any(skill IN p.skills WHERE skill = 'Python')
RETURN p.name

// No elements match
MATCH (p:Person)
WHERE none(skill IN p.skills WHERE skill = 'COBOL')
RETURN p.name

// Single element matches
MATCH (p:Person)
WHERE single(skill IN p.skills WHERE skill = 'Go')
RETURN p.name
```

### NULL Checking

```cypher
// Property is null (doesn't exist)
MATCH (p:Person)
WHERE p.email IS NULL
RETURN p.name

// Property exists
MATCH (p:Person)
WHERE p.email IS NOT NULL
RETURN p.name, p.email

// Combine with other conditions
MATCH (p:Person)
WHERE p.email IS NOT NULL AND p.email ENDS WITH '@company.com'
RETURN p.name
```

### Filtering on Labels

```cypher
// Check if node has label
MATCH (n)
WHERE n:Person
RETURN n.name

// Check for specific label
MATCH (p:Person)
WHERE p:Employee  // Additional label check
RETURN p.name

// Exclude nodes with label
MATCH (p:Person)
WHERE NOT p:Contractor
RETURN p.name
```

### Filtering on Relationships

```cypher
// Check if relationship exists
MATCH (p:Person)
WHERE EXISTS { (p)-[:WORKS_FOR]->(:Company) }
RETURN p.name

// Count relationships
MATCH (p:Person)
WHERE COUNT { (p)-[:KNOWS]->() } >= 5
RETURN p.name AS popular

// Check relationship doesn't exist
MATCH (p:Person)
WHERE NOT EXISTS { (p)-[:KNOWS]->(:Person {name: 'Alice'}) }
RETURN p.name
```

### Filtering on Paths

```cypher
// Filter by path length
MATCH path = (a:Person)-[:KNOWS*]->(b:Person)
WHERE length(path) <= 3
RETURN path

// Filter by properties in path
MATCH path = (a:Person)-[rels:KNOWS*]->(b:Person)
WHERE all(r IN rels WHERE r.since > 2015)
RETURN path
```

---

## 5.3 The RETURN Clause

### Purpose

`RETURN` specifies what to output from the query.

### Returning Different Elements

```cypher
// Return nodes
MATCH (p:Person)
RETURN p

// Return relationships
MATCH ()-[r:KNOWS]->()
RETURN r

// Return paths
MATCH path = (a)-[*]->(b)
RETURN path

// Return specific properties
MATCH (p:Person)
RETURN p.name, p.age

// Return everything matched
MATCH (p:Person)-[r:KNOWS]->(f:Person)
RETURN *
```

### Aliases (AS)

```cypher
// Simple alias
MATCH (p:Person)
RETURN p.name AS personName

// Multiple aliases
MATCH (p:Person)-[:WORKS_FOR]->(c:Company)
RETURN p.name AS employee,
       c.name AS employer,
       p.startDate AS joinDate

// Required for expressions
MATCH (p:Person)
RETURN p.firstName + ' ' + p.lastName AS fullName

// Alias for calculations
MATCH (p:Product)
RETURN p.name,
       p.price AS originalPrice,
       p.price * 0.9 AS discountedPrice
```

### Expressions in RETURN

```cypher
// String concatenation
MATCH (p:Person)
RETURN p.firstName + ' ' + p.lastName AS fullName

// Mathematical expressions
MATCH (o:Order)
RETURN o.id,
       o.quantity * o.unitPrice AS subtotal,
       o.quantity * o.unitPrice * 1.08 AS totalWithTax

// Conditional expressions
MATCH (p:Person)
RETURN p.name,
       CASE 
         WHEN p.age < 18 THEN 'Minor'
         WHEN p.age < 65 THEN 'Adult'
         ELSE 'Senior'
       END AS ageGroup

// Function calls
MATCH (p:Person)
RETURN p.name,
       toUpper(p.name) AS upperName,
       size(p.name) AS nameLength
```

### Returning Collections

```cypher
// Return as list
MATCH (p:Person)-[:KNOWS]->(f:Person)
RETURN p.name, collect(f.name) AS friends

// Return as map
MATCH (p:Person)
RETURN {name: p.name, age: p.age, city: p.city} AS personInfo

// Return properties as map
MATCH (p:Person {name: 'Alice'})
RETURN properties(p) AS allProperties

// Return specific keys
MATCH (p:Person)
RETURN p {.name, .age} AS subset
```

### DISTINCT

```cypher
// Remove duplicate rows
MATCH (p:Person)-[:LIVES_IN]->(c:City)
RETURN DISTINCT c.name

// Distinct with multiple columns
MATCH (p:Person)-[:WORKS_FOR]->(c:Company)
RETURN DISTINCT p.department, c.name

// Count distinct values
MATCH (p:Person)
RETURN count(DISTINCT p.city) AS uniqueCities
```

---

## 5.4 OPTIONAL MATCH

### Purpose

`OPTIONAL MATCH` is like MATCH, but returns NULL for missing patterns instead of excluding the row.

### Comparison: MATCH vs OPTIONAL MATCH

```cypher
// MATCH: Only returns people who have an email
MATCH (p:Person)
WHERE p.email IS NOT NULL
RETURN p.name, p.email

// OPTIONAL MATCH: Returns all people, NULL for missing relationships
MATCH (p:Person)
OPTIONAL MATCH (p)-[:WORKS_FOR]->(c:Company)
RETURN p.name, c.name AS company  -- company is NULL if no relationship
```

### Use Cases

```cypher
// Include all people, even those without friends
MATCH (p:Person)
OPTIONAL MATCH (p)-[:KNOWS]->(friend:Person)
RETURN p.name, collect(friend.name) AS friends

// Left join style query
MATCH (c:Customer)
OPTIONAL MATCH (c)-[:PLACED]->(o:Order)
RETURN c.name, count(o) AS orderCount

// Multiple optional matches
MATCH (p:Person)
OPTIONAL MATCH (p)-[:WORKS_FOR]->(company:Company)
OPTIONAL MATCH (p)-[:LIVES_IN]->(city:City)
RETURN p.name, company.name, city.name
```

### COALESCE with OPTIONAL MATCH

```cypher
// Provide default values for nulls
MATCH (p:Person)
OPTIONAL MATCH (p)-[:LIVES_IN]->(c:City)
RETURN p.name,
       coalesce(c.name, 'Unknown') AS city

// Default for missing relationship properties
MATCH (p:Person)
OPTIONAL MATCH (p)-[r:WORKS_FOR]->(c:Company)
RETURN p.name,
       coalesce(c.name, 'Unemployed') AS employer,
       coalesce(r.since, 'N/A') AS startDate
```

---

## 5.5 Sorting and Pagination

### ORDER BY

```cypher
// Sort ascending (default)
MATCH (p:Person)
RETURN p.name, p.age
ORDER BY p.age

// Sort descending
MATCH (p:Person)
RETURN p.name, p.age
ORDER BY p.age DESC

// Multiple sort criteria
MATCH (p:Person)
RETURN p.name, p.department, p.salary
ORDER BY p.department ASC, p.salary DESC

// Sort by expression
MATCH (p:Person)
RETURN p.firstName, p.lastName
ORDER BY p.lastName + ', ' + p.firstName

// Sort by alias
MATCH (p:Person)
RETURN p.name, p.age * 12 AS ageInMonths
ORDER BY ageInMonths DESC

// NULL handling in sort
MATCH (p:Person)
RETURN p.name, p.middleName
ORDER BY p.middleName  -- NULLs come last in ASC, first in DESC
```

### LIMIT

```cypher
// Return first N results
MATCH (p:Person)
RETURN p.name
LIMIT 10

// Combined with ORDER BY
MATCH (p:Person)
RETURN p.name, p.salary
ORDER BY p.salary DESC
LIMIT 5  -- Top 5 earners
```

### SKIP

```cypher
// Skip first N results
MATCH (p:Person)
RETURN p.name
SKIP 10

// Pagination (page 3, 10 items per page)
MATCH (p:Person)
RETURN p.name
ORDER BY p.name
SKIP 20  -- Skip first 2 pages
LIMIT 10 -- Take 10 items
```

### Pagination Pattern

```cypher
// Parameterized pagination
// :params {pageSize: 10, pageNumber: 3}

MATCH (p:Person)
RETURN p.name, p.age
ORDER BY p.name
SKIP $pageSize * ($pageNumber - 1)
LIMIT $pageSize
```

---

## 5.6 Practical Query Examples

### Example 1: Social Network Queries

```cypher
// Setup data
CREATE (alice:Person {name: 'Alice', age: 30, city: 'NYC'})
CREATE (bob:Person {name: 'Bob', age: 28, city: 'LA'})
CREATE (charlie:Person {name: 'Charlie', age: 35, city: 'NYC'})
CREATE (diana:Person {name: 'Diana', age: 25, city: 'Chicago'})
CREATE (eve:Person {name: 'Eve', age: 32, city: 'NYC'})

CREATE (alice)-[:KNOWS {since: 2015}]->(bob)
CREATE (alice)-[:KNOWS {since: 2018}]->(charlie)
CREATE (bob)-[:KNOWS {since: 2016}]->(charlie)
CREATE (bob)-[:KNOWS {since: 2019}]->(diana)
CREATE (charlie)-[:KNOWS {since: 2020}]->(diana)
CREATE (charlie)-[:KNOWS {since: 2017}]->(eve)

// Find Alice's direct friends
MATCH (alice:Person {name: 'Alice'})-[:KNOWS]->(friend)
RETURN friend.name, friend.city

// Find Alice's friends of friends (excluding Alice and direct friends)
MATCH (alice:Person {name: 'Alice'})-[:KNOWS]->(friend)-[:KNOWS]->(fof)
WHERE fof <> alice 
  AND NOT (alice)-[:KNOWS]->(fof)
RETURN DISTINCT fof.name

// Find mutual friends between Alice and Diana
MATCH (alice:Person {name: 'Alice'})-[:KNOWS]-(mutual)-[:KNOWS]-(diana:Person {name: 'Diana'})
RETURN DISTINCT mutual.name

// Find people who know each other (both directions)
MATCH (a:Person)-[:KNOWS]->(b:Person)-[:KNOWS]->(a)
RETURN DISTINCT a.name, b.name

// Find the most connected person
MATCH (p:Person)-[:KNOWS]-(other)
RETURN p.name, count(other) AS connections
ORDER BY connections DESC
LIMIT 1
```

### Example 2: E-commerce Queries

```cypher
// Setup data
CREATE (electronics:Category {name: 'Electronics'})
CREATE (clothing:Category {name: 'Clothing'})

CREATE (laptop:Product {name: 'Laptop', price: 999, stock: 50})
CREATE (phone:Product {name: 'Phone', price: 699, stock: 100})
CREATE (shirt:Product {name: 'T-Shirt', price: 29, stock: 200})

CREATE (laptop)-[:IN_CATEGORY]->(electronics)
CREATE (phone)-[:IN_CATEGORY]->(electronics)
CREATE (shirt)-[:IN_CATEGORY]->(clothing)

CREATE (alice:Customer {name: 'Alice', email: 'alice@email.com'})
CREATE (bob:Customer {name: 'Bob', email: 'bob@email.com'})

CREATE (alice)-[:PURCHASED {date: date('2024-01-15'), quantity: 1}]->(laptop)
CREATE (alice)-[:PURCHASED {date: date('2024-01-20'), quantity: 2}]->(shirt)
CREATE (bob)-[:PURCHASED {date: date('2024-01-18'), quantity: 1}]->(phone)
CREATE (bob)-[:PURCHASED {date: date('2024-01-22'), quantity: 1}]->(laptop)

// Find all products in Electronics category
MATCH (p:Product)-[:IN_CATEGORY]->(c:Category {name: 'Electronics'})
RETURN p.name, p.price
ORDER BY p.price DESC

// Find customers who purchased Electronics
MATCH (customer:Customer)-[:PURCHASED]->(product:Product)-[:IN_CATEGORY]->(c:Category {name: 'Electronics'})
RETURN DISTINCT customer.name, collect(product.name) AS products

// Calculate total spent by each customer
MATCH (customer:Customer)-[purchase:PURCHASED]->(product:Product)
RETURN customer.name,
       sum(purchase.quantity * product.price) AS totalSpent
ORDER BY totalSpent DESC

// Find products often purchased together
MATCH (p1:Product)<-[:PURCHASED]-(customer)-[:PURCHASED]->(p2:Product)
WHERE p1 <> p2
RETURN p1.name, p2.name, count(*) AS timesTogether
ORDER BY timesTogether DESC

// Recommend products (bought by others who bought same items)
MATCH (alice:Customer {name: 'Alice'})-[:PURCHASED]->(product)<-[:PURCHASED]-(other:Customer)
MATCH (other)-[:PURCHASED]->(recommended:Product)
WHERE NOT (alice)-[:PURCHASED]->(recommended)
RETURN DISTINCT recommended.name
```

### Example 3: Movie Database Queries

```cypher
// Find movies directed by Christopher Nolan
MATCH (nolan:Person {name: 'Christopher Nolan'})-[:DIRECTED]->(movie:Movie)
RETURN movie.title, movie.released
ORDER BY movie.released

// Find actors who worked with Nolan
MATCH (nolan:Person {name: 'Christopher Nolan'})-[:DIRECTED]->(movie)<-[:ACTED_IN]-(actor:Person)
RETURN DISTINCT actor.name

// Find actors who appeared in multiple movies together
MATCH (a1:Person)-[:ACTED_IN]->(m:Movie)<-[:ACTED_IN]-(a2:Person)
WHERE a1.name < a2.name  // Avoid duplicates
WITH a1, a2, count(m) AS moviesTogether
WHERE moviesTogether > 1
RETURN a1.name, a2.name, moviesTogether
ORDER BY moviesTogether DESC

// Find "Six Degrees of Kevin Bacon"
MATCH path = shortestPath(
  (kevin:Person {name: 'Kevin Bacon'})-[:ACTED_IN*]-(other:Person)
)
WHERE other.name = 'Tom Hanks'
RETURN length(path) / 2 AS baconNumber,
       [node IN nodes(path) WHERE node:Movie | node.title] AS movies
```

---

## 5.7 Performance Tips for Reading

### Use Indexes

```cypher
// Create index for frequently queried properties
CREATE INDEX person_name_index FOR (p:Person) ON (p.name)

// Query will use the index automatically
MATCH (p:Person {name: 'Alice'})
RETURN p
```

### Limit Early

```cypher
// Instead of this (processes all, then limits)
MATCH (p:Person)
WHERE p.age > 25
RETURN p.name
ORDER BY p.name
LIMIT 10

// Use LIMIT with specific starting point if possible
MATCH (p:Person {name: 'Alice'})-[:KNOWS*1..3]-(friend)
RETURN DISTINCT friend.name
LIMIT 100
```

### Avoid Cartesian Products

```cypher
// ❌ Bad: Creates cartesian product
MATCH (p:Person), (c:Company)
RETURN p.name, c.name

// ✅ Good: Connected pattern
MATCH (p:Person)-[:WORKS_FOR]->(c:Company)
RETURN p.name, c.name
```

### Be Specific with Labels

```cypher
// ❌ Slower: No label
MATCH (n {name: 'Alice'})
RETURN n

// ✅ Faster: With label
MATCH (p:Person {name: 'Alice'})
RETURN p
```

---

## Summary

### Key Takeaways

1. **MATCH** finds patterns in the graph
2. **WHERE** filters results with conditions
3. **RETURN** specifies output, use aliases for expressions
4. **OPTIONAL MATCH** includes rows with missing patterns (returns NULL)
5. **ORDER BY, SKIP, LIMIT** for sorting and pagination

### Quick Reference

```cypher
MATCH (n:Label {prop: value})          -- Find nodes
MATCH (a)-[r:TYPE]->(b)                -- Find relationships
WHERE condition                        -- Filter
OPTIONAL MATCH pattern                 -- Null-safe match
RETURN expression AS alias             -- Output
ORDER BY column [ASC|DESC]             -- Sort
SKIP n LIMIT m                         -- Paginate
```

---

## Exercises

### Exercise 5.1: Basic MATCH
Write queries to:
1. Find all movies released after 2010
2. Find all people born in the 1980s
3. Find all products in a specific category

### Exercise 5.2: Complex WHERE
Write queries using WHERE to:
1. Find people whose name starts with 'J' and ends with 'n'
2. Find products priced between $50 and $100 in specific categories
3. Find people who have both email and phone properties

### Exercise 5.3: Relationships
Write queries to:
1. Find all actors who acted in movies directed by a specific director
2. Find all customers who purchased products in multiple categories
3. Find people who are connected through exactly 2 intermediate people

### Exercise 5.4: OPTIONAL MATCH
Write queries using OPTIONAL MATCH to:
1. List all customers with their orders (including those with no orders)
2. Find all products with their reviews (including unreviewed products)
3. Show all employees with their managers (including those without managers)

### Exercise 5.5: Pagination
Implement paginated queries for:
1. A product listing with 20 items per page
2. A user directory sorted alphabetically
3. A transaction history sorted by date descending

---

**Next Chapter: [Chapter 6: Cypher - Writing Data](06-cypher-writing-data.md)**
