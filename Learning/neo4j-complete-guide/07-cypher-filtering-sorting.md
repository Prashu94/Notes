# Chapter 7: Cypher - Filtering and Sorting (Advanced WHERE, ORDER BY, SKIP, LIMIT)

## Learning Objectives
By the end of this chapter, you will:
- Master advanced WHERE clause patterns
- Use ORDER BY with complex expressions
- Implement efficient pagination
- Understand performance implications of filtering

---

## 7.1 Advanced WHERE Patterns

### Pattern Existence Checks

```cypher
// Check if a pattern exists
MATCH (p:Person)
WHERE EXISTS { (p)-[:WORKS_FOR]->(:Company) }
RETURN p.name AS employed

// Check if pattern doesn't exist
MATCH (p:Person)
WHERE NOT EXISTS { (p)-[:WORKS_FOR]->(:Company) }
RETURN p.name AS unemployed

// Count pattern occurrences
MATCH (p:Person)
WHERE COUNT { (p)-[:KNOWS]->(:Person) } >= 5
RETURN p.name AS popular

// Exists with conditions
MATCH (p:Person)
WHERE EXISTS {
    MATCH (p)-[:PURCHASED]->(product:Product)
    WHERE product.price > 100
}
RETURN p.name AS bigSpender
```

### Subquery Filters

```cypher
// Filter using subquery result
MATCH (p:Person)
WHERE p.salary > (
    CALL {
        MATCH (e:Person)
        RETURN avg(e.salary) AS avgSalary
    }
    RETURN avgSalary
)
RETURN p.name, p.salary AS aboveAverage

// Exists subquery with complex condition
MATCH (customer:Customer)
WHERE EXISTS {
    MATCH (customer)-[:PLACED]->(order:Order)
    WHERE order.total > 1000
      AND order.date > date() - duration('P30D')
}
RETURN customer.name
```

### List Predicate Functions

```cypher
// ALL: every element must satisfy
MATCH (p:Person)
WHERE all(skill IN p.skills WHERE skill STARTS WITH 'Java')
RETURN p.name AS javaExperts

// ANY: at least one element must satisfy
MATCH (p:Person)
WHERE any(skill IN p.skills WHERE skill CONTAINS 'Python')
RETURN p.name AS pythonKnowers

// NONE: no elements satisfy
MATCH (p:Person)
WHERE none(skill IN p.skills WHERE skill = 'COBOL')
RETURN p.name AS notCobolProgrammers

// SINGLE: exactly one element satisfies
MATCH (p:Person)
WHERE single(lang IN p.languages WHERE lang = 'English')
RETURN p.name AS onlyEnglishSpeakers

// Combine predicates
MATCH (p:Person)
WHERE any(skill IN p.skills WHERE skill STARTS WITH 'Java')
  AND all(cert IN p.certifications WHERE cert.year > 2020)
RETURN p.name
```

### Range and Boundary Checks

```cypher
// Value in range
MATCH (p:Product)
WHERE 50 <= p.price <= 100
RETURN p.name, p.price

// Date ranges
MATCH (o:Order)
WHERE date('2024-01-01') <= o.orderDate <= date('2024-12-31')
RETURN o.id, o.orderDate

// Using duration
MATCH (o:Order)
WHERE o.orderDate >= date() - duration('P30D')
RETURN o.id AS recentOrders

// Exclusive bounds
MATCH (p:Product)
WHERE p.price > 50 AND p.price < 100
RETURN p.name
```

### Regular Expressions

```cypher
// Basic regex
MATCH (p:Person)
WHERE p.name =~ 'A.*'  -- Starts with A
RETURN p.name

// Case insensitive
MATCH (p:Person)
WHERE p.name =~ '(?i)alice'  -- Any case
RETURN p.name

// Pattern alternatives
MATCH (p:Person)
WHERE p.email =~ '.*@(gmail|yahoo|hotmail)\\.com'
RETURN p.name, p.email

// Digit patterns
MATCH (p:Product)
WHERE p.sku =~ 'SKU-[0-9]{6}'  -- SKU followed by 6 digits
RETURN p.name, p.sku

// Complex patterns
MATCH (p:Person)
WHERE p.phone =~ '\\+?[0-9]{1,3}[-. ]?\\([0-9]{3}\\)[-. ]?[0-9]{3}[-. ]?[0-9]{4}'
RETURN p.name, p.phone AS validPhone
```

### NULL-safe Comparisons

```cypher
// Coalesce for defaults
MATCH (p:Person)
WHERE coalesce(p.middleName, '') <> ''
RETURN p.name, p.middleName

// Handle potential nulls in comparisons
MATCH (p:Product)
WHERE coalesce(p.discount, 0) > 0
RETURN p.name, p.discount

// Filter considering nulls
MATCH (p:Person)
WHERE p.email IS NOT NULL 
  AND p.email CONTAINS '@'
  AND NOT p.email STARTS WITH '@'
RETURN p.email
```

---

## 7.2 Filtering on Graph Structure

### Filtering by Degree (Connection Count)

```cypher
// Filter by number of relationships
MATCH (p:Person)
WHERE COUNT { (p)-[:KNOWS]->() } >= 5
RETURN p.name AS popular

// Filter by incoming relationships
MATCH (p:Product)
WHERE COUNT { ()-[:PURCHASED]->(p) } >= 10
RETURN p.name AS bestSeller

// Filter by relationship in both directions
MATCH (p:Person)
WHERE COUNT { (p)-[:KNOWS]-() } >= 10
RETURN p.name AS wellConnected
```

### Filtering by Path Properties

```cypher
// Filter paths by total weight
MATCH path = (start:City {name: 'NYC'})-[:ROAD*]->(end:City {name: 'LA'})
WHERE reduce(total = 0, r IN relationships(path) | total + r.distance) < 3000
RETURN path, reduce(total = 0, r IN relationships(path) | total + r.distance) AS totalDistance

// Filter by all relationships in path
MATCH path = (a:Person)-[:KNOWS*1..4]->(b:Person)
WHERE a.name = 'Alice'
  AND all(r IN relationships(path) WHERE r.since > 2015)
RETURN path

// Filter by any node in path
MATCH path = (a:Person)-[*1..5]->(b:Person)
WHERE a.name = 'Alice'
  AND any(n IN nodes(path) WHERE n:Influencer)
RETURN path
```

### Filtering by Labels

```cypher
// Check specific label
MATCH (n)
WHERE n:Person
RETURN n.name

// Multiple label check (AND)
MATCH (n)
WHERE n:Person AND n:Employee
RETURN n.name

// Multiple label check (OR)
MATCH (n)
WHERE n:Person OR n:Company
RETURN n

// Exclude nodes with specific label
MATCH (p:Person)
WHERE NOT p:Temporary
RETURN p.name

// Dynamic label check
MATCH (n)
WHERE 'Person' IN labels(n)
RETURN n
```

---

## 7.3 ORDER BY Deep Dive

### Basic Ordering

```cypher
// Ascending (default)
MATCH (p:Person)
RETURN p.name
ORDER BY p.name

-- Explicit ascending
MATCH (p:Person)
RETURN p.name
ORDER BY p.name ASC

-- Descending
MATCH (p:Person)
RETURN p.name, p.age
ORDER BY p.age DESC
```

### Multiple Sort Criteria

```cypher
// Primary and secondary sort
MATCH (e:Employee)
RETURN e.name, e.department, e.salary
ORDER BY e.department ASC, e.salary DESC

// Three-level sort
MATCH (p:Product)
RETURN p.category, p.brand, p.name, p.price
ORDER BY p.category, p.brand, p.price DESC
```

### Ordering by Expressions

```cypher
// Order by calculated value
MATCH (p:Product)
RETURN p.name, p.price, p.price * 1.1 AS priceWithTax
ORDER BY priceWithTax DESC

// Order by string length
MATCH (p:Person)
RETURN p.name
ORDER BY size(p.name) DESC

// Order by aggregation
MATCH (c:Customer)-[:PURCHASED]->(p:Product)
RETURN c.name, sum(p.price) AS totalSpent
ORDER BY totalSpent DESC

// Order by case expression
MATCH (p:Person)
RETURN p.name, p.status,
       CASE p.status
         WHEN 'VIP' THEN 1
         WHEN 'Regular' THEN 2
         ELSE 3
       END AS statusRank
ORDER BY statusRank, p.name
```

### NULL Handling in ORDER BY

```cypher
// By default: ASC puts NULLs last, DESC puts NULLs first
MATCH (p:Person)
RETURN p.name, p.middleName
ORDER BY p.middleName

// Explicit NULL handling using COALESCE
MATCH (p:Person)
RETURN p.name, p.middleName
ORDER BY coalesce(p.middleName, 'ZZZZZ')  -- NULLs at end

// Put NULLs first in ASC order
MATCH (p:Person)
RETURN p.name, p.middleName
ORDER BY 
    CASE WHEN p.middleName IS NULL THEN 0 ELSE 1 END,
    p.middleName
```

### Order by Relationship Properties

```cypher
// Order by relationship property
MATCH (a:Person)-[r:KNOWS]->(b:Person)
WHERE a.name = 'Alice'
RETURN b.name, r.since
ORDER BY r.since DESC

// Order by path length
MATCH path = (a:Person {name: 'Alice'})-[:KNOWS*]->(b:Person)
RETURN b.name, length(path) AS distance
ORDER BY distance
```

---

## 7.4 Pagination with SKIP and LIMIT

### Basic Pagination

```cypher
// First page (items 1-10)
MATCH (p:Product)
RETURN p.name, p.price
ORDER BY p.name
LIMIT 10

// Second page (items 11-20)
MATCH (p:Product)
RETURN p.name, p.price
ORDER BY p.name
SKIP 10
LIMIT 10

// Third page (items 21-30)
MATCH (p:Product)
RETURN p.name, p.price
ORDER BY p.name
SKIP 20
LIMIT 10
```

### Parameterized Pagination

```cypher
// Parameters: pageSize=10, pageNumber=3
:params {pageSize: 10, pageNumber: 3}

MATCH (p:Product)
RETURN p.name, p.price
ORDER BY p.name
SKIP $pageSize * ($pageNumber - 1)
LIMIT $pageSize
```

### Pagination with Total Count

```cypher
// Get page data with total count
MATCH (p:Product)
WITH p
ORDER BY p.name
WITH collect(p) AS allProducts, count(p) AS total
UNWIND allProducts[20..30] AS product  // Items 21-30
RETURN product.name, product.price, total AS totalProducts
```

### Cursor-Based Pagination (Keyset)

```cypher
// Better performance for large datasets
// First page
MATCH (p:Product)
WHERE p.name > ''  // Start condition
RETURN p.id, p.name, p.price
ORDER BY p.name
LIMIT 10

// Next page (using last item from previous page)
// :param lastSeen => 'LastProductName'
MATCH (p:Product)
WHERE p.name > $lastSeen
RETURN p.id, p.name, p.price
ORDER BY p.name
LIMIT 10
```

### SKIP/LIMIT Performance Considerations

```cypher
// ❌ Slow for large offsets (scans all skipped rows)
MATCH (p:Product)
RETURN p.name
ORDER BY p.name
SKIP 1000000
LIMIT 10

// ✅ Better: Cursor-based pagination
MATCH (p:Product)
WHERE p.name > $lastSeenName
RETURN p.name
ORDER BY p.name
LIMIT 10

// ✅ Or filter first, then paginate
MATCH (p:Product)
WHERE p.category = 'Electronics'
RETURN p.name
ORDER BY p.name
SKIP 100
LIMIT 10
```

---

## 7.5 WITH for Intermediate Filtering

### Chaining Filters with WITH

```cypher
// Filter in stages
MATCH (p:Person)
WHERE p.age > 25
WITH p
WHERE p.city = 'NYC'
WITH p
ORDER BY p.salary DESC
LIMIT 10
RETURN p.name, p.salary

// Aggregate then filter
MATCH (c:Customer)-[:PURCHASED]->(p:Product)
WITH c, count(p) AS purchaseCount, sum(p.price) AS totalSpent
WHERE purchaseCount >= 5 AND totalSpent > 500
RETURN c.name, purchaseCount, totalSpent
ORDER BY totalSpent DESC
```

### Filter After Aggregation

```cypher
// Find customers with high average order value
MATCH (c:Customer)-[:PLACED]->(o:Order)
WITH c, avg(o.total) AS avgOrderValue
WHERE avgOrderValue > 100
RETURN c.name, avgOrderValue
ORDER BY avgOrderValue DESC

// Find products in multiple categories
MATCH (p:Product)-[:IN_CATEGORY]->(cat:Category)
WITH p, collect(cat.name) AS categories, count(cat) AS catCount
WHERE catCount >= 2
RETURN p.name, categories
```

### HAVING-equivalent Pattern

```cypher
-- SQL: HAVING count(*) > 5
-- Cypher:
MATCH (city:City)<-[:LIVES_IN]-(p:Person)
WITH city, count(p) AS population
WHERE population > 1000000
RETURN city.name, population
ORDER BY population DESC
```

---

## 7.6 Efficient Filtering Patterns

### Use Indexes for Initial Filters

```cypher
// Create indexes for commonly filtered properties
CREATE INDEX product_category FOR (p:Product) ON (p.category)
CREATE INDEX product_price FOR (p:Product) ON (p.price)

// Query will use index
MATCH (p:Product)
WHERE p.category = 'Electronics'  -- Uses index
  AND p.price > 100               -- Further filters
RETURN p.name, p.price
```

### Filter Order Matters

```cypher
// ✅ More selective filter first (with index)
MATCH (p:Person)
WHERE p.email = 'alice@example.com'  -- Very selective, use index
  AND p.age > 25                      -- Less selective
RETURN p

// The query planner usually optimizes this, but be aware
```

### Avoid Expensive Patterns in WHERE

```cypher
// ❌ Expensive: calculating in WHERE
MATCH (p:Person)-[:KNOWS]-(friend)
WHERE size(collect(friend.name)) > 5
RETURN p

// ✅ Better: Use COUNT pattern
MATCH (p:Person)
WHERE COUNT { (p)-[:KNOWS]-() } > 5
RETURN p

// ❌ Expensive: pattern in WHERE
MATCH (p:Person)
WHERE (p)-[:KNOWS]->(:Celebrity)
RETURN p

// ✅ Better: Use EXISTS
MATCH (p:Person)
WHERE EXISTS { (p)-[:KNOWS]->(:Celebrity) }
RETURN p
```

### Combining Filters Efficiently

```cypher
// Use AND for multiple conditions on same pattern
MATCH (p:Person)-[r:WORKS_FOR]->(c:Company)
WHERE p.age > 25 
  AND r.startDate > date('2020-01-01')
  AND c.industry = 'Technology'
RETURN p.name, c.name

// Use pattern matching instead of multiple WHERE conditions
MATCH (p:Person {city: 'NYC', status: 'Active'})-[:WORKS_FOR]->(c:Company {industry: 'Tech'})
RETURN p.name, c.name
```

---

## 7.7 Full-Text Search Filtering

### Setup Full-Text Index

```cypher
// Create full-text index
CREATE FULLTEXT INDEX product_search FOR (p:Product) ON EACH [p.name, p.description]

// Create for multiple labels
CREATE FULLTEXT INDEX content_search FOR (n:Article|Blog|News) ON EACH [n.title, n.content]
```

### Full-Text Search Queries

```cypher
// Basic search
CALL db.index.fulltext.queryNodes('product_search', 'laptop computer')
YIELD node, score
RETURN node.name, score
ORDER BY score DESC
LIMIT 10

// Fuzzy search
CALL db.index.fulltext.queryNodes('product_search', 'labtop~')  -- Fuzzy match
YIELD node, score
RETURN node.name, score

// Phrase search
CALL db.index.fulltext.queryNodes('product_search', '"gaming laptop"')
YIELD node, score
RETURN node.name, score

// Boolean operators
CALL db.index.fulltext.queryNodes('product_search', 'laptop AND NOT refurbished')
YIELD node, score
RETURN node.name, score

// Combine with regular filtering
CALL db.index.fulltext.queryNodes('product_search', 'laptop')
YIELD node AS product, score
WHERE product.price < 1000 AND product.inStock = true
RETURN product.name, product.price, score
ORDER BY score DESC
```

---

## Summary

### Key Takeaways

1. **Pattern existence**: Use `EXISTS { }` and `COUNT { }` for subqueries
2. **List predicates**: `all()`, `any()`, `none()`, `single()` for list filtering
3. **ORDER BY**: Supports expressions, multiple columns, NULL handling
4. **Pagination**: SKIP/LIMIT for offset-based, cursor-based for large datasets
5. **WITH**: Enables filtering after aggregation (like HAVING)

### Quick Reference

```cypher
-- Pattern exists
WHERE EXISTS { (n)-[:REL]->() }
WHERE COUNT { (n)-[:REL]->() } > 5

-- List predicates
WHERE all(x IN list WHERE condition)
WHERE any(x IN list WHERE condition)

-- Order by multiple columns
ORDER BY col1 ASC, col2 DESC

-- Pagination
SKIP 20 LIMIT 10

-- Filter after aggregation
WITH n, count(*) AS cnt
WHERE cnt > 5
RETURN n, cnt
```

---

## Exercises

### Exercise 7.1: Advanced WHERE
1. Find all people who know at least 3 people who work at the same company
2. Find products where all reviews are 4 stars or higher
3. Find customers who haven't made a purchase in the last 30 days

### Exercise 7.2: Complex Ordering
1. Order products by category name, then by price descending
2. Create a "relevance score" based on multiple factors and order by it
3. Handle sorting with NULL values appropriately

### Exercise 7.3: Pagination Implementation
1. Implement cursor-based pagination for a product catalog
2. Return paginated results with total count
3. Compare performance of SKIP/LIMIT vs cursor-based for large offsets

### Exercise 7.4: Full-Text Search
1. Create a full-text index for searching articles by title and body
2. Implement search with relevance scoring
3. Combine full-text search with category filtering

---

**Next Chapter: [Chapter 8: Cypher - Aggregations](08-cypher-aggregations.md)**
