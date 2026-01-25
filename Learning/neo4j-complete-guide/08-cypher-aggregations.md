# Chapter 8: Cypher - Aggregations (COUNT, SUM, AVG, COLLECT, Grouping)

## Learning Objectives
By the end of this chapter, you will:
- Use all aggregation functions in Cypher
- Understand implicit grouping behavior
- Use COLLECT to create lists
- Apply aggregations with filtering
- Handle NULL values in aggregations

---

## 8.1 Introduction to Aggregations

### How Aggregation Works in Cypher

Unlike SQL, Cypher uses **implicit grouping**. Any non-aggregated return items automatically become grouping keys.

```cypher
// SQL equivalent would require GROUP BY
-- SQL: SELECT department, COUNT(*) FROM employees GROUP BY department

// Cypher: Automatic grouping
MATCH (e:Employee)
RETURN e.department, count(e) AS employeeCount
// e.department is automatically used for grouping
```

### Basic Aggregation Functions

| Function | Description |
|----------|-------------|
| `count(expr)` | Count non-null values |
| `count(*)` | Count all rows |
| `sum(expr)` | Sum of numeric values |
| `avg(expr)` | Average of numeric values |
| `min(expr)` | Minimum value |
| `max(expr)` | Maximum value |
| `collect(expr)` | Collect values into a list |
| `stdev(expr)` | Standard deviation |
| `stdevp(expr)` | Population standard deviation |
| `percentileCont(expr, p)` | Continuous percentile |
| `percentileDisc(expr, p)` | Discrete percentile |

---

## 8.2 COUNT Function

### Basic COUNT Usage

```cypher
// Count all nodes
MATCH (n)
RETURN count(n) AS totalNodes

// Count specific label
MATCH (p:Person)
RETURN count(p) AS personCount

// Count with pattern
MATCH (:Person)-[r:KNOWS]->(:Person)
RETURN count(r) AS friendships

// Count distinct values
MATCH (p:Person)
RETURN count(DISTINCT p.city) AS uniqueCities
```

### COUNT(*) vs COUNT(expression)

```cypher
// COUNT(*) counts all rows
MATCH (p:Person)
RETURN count(*) AS totalRows

// COUNT(expr) counts non-NULL values only
MATCH (p:Person)
RETURN count(p.middleName) AS withMiddleName
// Only counts people who have middleName property

// Difference example
MATCH (p:Person)
RETURN 
    count(*) AS allPeople,
    count(p.email) AS withEmail,
    count(DISTINCT p.city) AS uniqueCities
```

### COUNT with Grouping

```cypher
// Count per group
MATCH (e:Employee)
RETURN e.department, count(e) AS employeeCount

// Count with multiple groups
MATCH (p:Product)-[:IN_CATEGORY]->(c:Category)
RETURN c.name AS category, p.brand, count(p) AS productCount
ORDER BY category, productCount DESC

// Count relationships per node
MATCH (p:Person)-[r:KNOWS]-()
RETURN p.name, count(r) AS connections
ORDER BY connections DESC
```

### Conditional Counting

```cypher
// Count with condition
MATCH (o:Order)
RETURN 
    count(o) AS totalOrders,
    count(CASE WHEN o.status = 'Completed' THEN 1 END) AS completedOrders,
    count(CASE WHEN o.status = 'Pending' THEN 1 END) AS pendingOrders

// Alternative using SUM
MATCH (o:Order)
RETURN 
    sum(CASE WHEN o.status = 'Completed' THEN 1 ELSE 0 END) AS completed,
    sum(CASE WHEN o.status = 'Pending' THEN 1 ELSE 0 END) AS pending
```

---

## 8.3 SUM, AVG, MIN, MAX

### SUM Function

```cypher
// Total of a property
MATCH (o:Order)
RETURN sum(o.total) AS totalRevenue

// Sum with grouping
MATCH (c:Customer)-[:PLACED]->(o:Order)
RETURN c.name, sum(o.total) AS customerTotal
ORDER BY customerTotal DESC

// Sum calculated values
MATCH (o:Order)-[:CONTAINS]->(p:Product)
RETURN sum(p.price * p.quantity) AS totalValue
```

### AVG Function

```cypher
// Simple average
MATCH (p:Product)
RETURN avg(p.price) AS averagePrice

// Average with grouping
MATCH (e:Employee)
RETURN e.department, avg(e.salary) AS avgSalary
ORDER BY avgSalary DESC

// Average of calculated expression
MATCH (p:Person)-[r:RATED]->(m:Movie)
RETURN m.title, avg(toFloat(r.rating)) AS avgRating, count(r) AS reviewCount
ORDER BY avgRating DESC
```

### MIN and MAX Functions

```cypher
// Simple min/max
MATCH (p:Product)
RETURN min(p.price) AS cheapest, max(p.price) AS mostExpensive

// Min/max with grouping
MATCH (e:Employee)
RETURN e.department, 
       min(e.salary) AS minSalary,
       max(e.salary) AS maxSalary,
       max(e.salary) - min(e.salary) AS salaryRange

// Min/max on dates
MATCH (o:Order)
RETURN min(o.orderDate) AS firstOrder, max(o.orderDate) AS latestOrder

// Min/max on strings (alphabetical)
MATCH (p:Person)
RETURN min(p.name) AS firstAlpha, max(p.name) AS lastAlpha
```

### Combining Aggregations

```cypher
// Multiple aggregations in one query
MATCH (p:Product)
RETURN 
    count(p) AS totalProducts,
    sum(p.price) AS totalValue,
    avg(p.price) AS avgPrice,
    min(p.price) AS minPrice,
    max(p.price) AS maxPrice

// With grouping
MATCH (o:Order)-[:CONTAINS]->(p:Product)
RETURN o.id,
       count(p) AS itemCount,
       sum(p.price) AS orderTotal,
       avg(p.price) AS avgItemPrice
```

---

## 8.4 Statistical Functions

### Standard Deviation

```cypher
// Sample standard deviation
MATCH (e:Employee)
RETURN 
    avg(e.salary) AS avgSalary,
    stdev(e.salary) AS salaryStdDev

// Population standard deviation
MATCH (e:Employee)
RETURN 
    avg(e.salary) AS avgSalary,
    stdevp(e.salary) AS populationStdDev

// Per group
MATCH (e:Employee)
RETURN e.department,
       avg(e.salary) AS avgSalary,
       stdev(e.salary) AS stdDev
ORDER BY stdDev DESC
```

### Percentiles

```cypher
// Median (50th percentile)
MATCH (p:Product)
RETURN percentileCont(p.price, 0.5) AS medianPrice

// Multiple percentiles
MATCH (e:Employee)
RETURN 
    percentileCont(e.salary, 0.25) AS q1,
    percentileCont(e.salary, 0.5) AS median,
    percentileCont(e.salary, 0.75) AS q3,
    percentileCont(e.salary, 0.9) AS p90

// Discrete vs Continuous
MATCH (r:Review)
RETURN 
    percentileDisc(r.rating, 0.5) AS medianRatingDiscrete,  -- Returns actual value
    percentileCont(r.rating, 0.5) AS medianRatingContinuous -- May interpolate
```

---

## 8.5 COLLECT - Creating Lists

### Basic COLLECT Usage

```cypher
// Collect values into list
MATCH (p:Person)
RETURN collect(p.name) AS allNames

// Collect with pattern
MATCH (p:Person)-[:KNOWS]->(friend:Person)
WHERE p.name = 'Alice'
RETURN collect(friend.name) AS aliceFriends

// Collect distinct values
MATCH (o:Order)-[:CONTAINS]->(p:Product)
RETURN collect(DISTINCT p.category) AS orderedCategories
```

### COLLECT with Grouping

```cypher
// Group and collect
MATCH (e:Employee)
RETURN e.department, collect(e.name) AS employees

// Collect with ordering (use ORDER BY before collect)
MATCH (e:Employee)
WITH e
ORDER BY e.name
RETURN e.department, collect(e.name) AS employeesAlphabetical

// Collect multiple properties
MATCH (e:Employee)
RETURN e.department, 
       collect({name: e.name, salary: e.salary}) AS employeeDetails
```

### Collecting Nodes and Relationships

```cypher
// Collect nodes
MATCH (c:Category)<-[:IN_CATEGORY]-(p:Product)
RETURN c.name, collect(p) AS products

// Collect relationships
MATCH (p:Person)-[r:REVIEWED]->(m:Movie)
RETURN m.title, collect(r) AS reviews

// Collect paths
MATCH path = (a:Person)-[:KNOWS*1..3]->(b:Person)
WHERE a.name = 'Alice'
RETURN collect(path) AS allPaths
```

### Limited COLLECT

```cypher
// Collect only first N items
MATCH (p:Product)
WITH p
ORDER BY p.sales DESC
WITH collect(p.name)[0..5] AS topProducts
RETURN topProducts

// Alternative using LIMIT before collect
MATCH (p:Product)
WITH p
ORDER BY p.sales DESC
LIMIT 5
RETURN collect(p.name) AS topProducts
```

---

## 8.6 Implicit Grouping Rules

### Understanding Grouping Behavior

```cypher
// Non-aggregated items become grouping keys
MATCH (e:Employee)
RETURN e.department, e.role, count(e) AS count
// Groups by: department AND role

// Single aggregation = one result row
MATCH (p:Person)
RETURN count(p) AS total
// No grouping, returns single row

// Node as grouping key
MATCH (d:Department)<-[:WORKS_IN]-(e:Employee)
RETURN d, count(e) AS employeeCount
// Groups by the entire department node
```

### Controlling Grouping

```cypher
// Group by specific properties
MATCH (p:Person)
RETURN p.city, p.country, count(p) AS residents

// Group by node ID
MATCH (c:Company)<-[:WORKS_FOR]-(e:Employee)
RETURN id(c) AS companyId, c.name, count(e) AS employees

// Use WITH to change grouping mid-query
MATCH (c:Customer)-[:PLACED]->(o:Order)
WITH c, count(o) AS orderCount  -- Group by customer
WHERE orderCount > 5
WITH count(c) AS loyalCustomers  -- Now aggregate all
RETURN loyalCustomers
```

---

## 8.7 HAVING Equivalent - Filtering Aggregations

### Filter After Aggregation with WITH

```cypher
// SQL HAVING equivalent
-- SQL: SELECT dept, COUNT(*) FROM emp GROUP BY dept HAVING COUNT(*) > 10

// Cypher:
MATCH (e:Employee)
WITH e.department AS dept, count(e) AS empCount
WHERE empCount > 10
RETURN dept, empCount

// Multiple conditions on aggregates
MATCH (c:Customer)-[:PLACED]->(o:Order)
WITH c, count(o) AS orderCount, sum(o.total) AS totalSpent
WHERE orderCount >= 5 AND totalSpent > 1000
RETURN c.name, orderCount, totalSpent
ORDER BY totalSpent DESC
```

### Complex Filtering Patterns

```cypher
// Filter based on aggregated list
MATCH (p:Person)-[:KNOWS]->(friend:Person)
WITH p, collect(friend.city) AS friendCities
WHERE size(friendCities) > 3
  AND 'NYC' IN friendCities
RETURN p.name, friendCities

// Filter using aggregated properties
MATCH (product:Product)-[:HAS_REVIEW]->(r:Review)
WITH product, avg(r.rating) AS avgRating, count(r) AS reviewCount
WHERE avgRating >= 4.0 AND reviewCount >= 10
RETURN product.name, avgRating, reviewCount
ORDER BY avgRating DESC
```

---

## 8.8 NULL Handling in Aggregations

### Default NULL Behavior

```cypher
// NULL values are typically ignored
MATCH (p:Person)
RETURN 
    count(p.salary) AS withSalary,      -- Counts non-NULL only
    count(*) AS totalPeople,             -- Counts all rows
    avg(p.salary) AS avgSalary           -- Ignores NULLs

// Explicit NULL handling
MATCH (p:Person)
RETURN 
    avg(coalesce(p.salary, 0)) AS avgWithZeroDefault,
    avg(p.salary) AS avgIgnoringNull
```

### Counting NULLs

```cypher
// Count NULL values
MATCH (p:Person)
RETURN 
    count(*) AS total,
    count(p.email) AS withEmail,
    count(*) - count(p.email) AS withoutEmail

// Alternative
MATCH (p:Person)
WHERE p.email IS NULL
RETURN count(p) AS missingEmail
```

### COLLECT and NULLs

```cypher
// COLLECT excludes NULLs by default
MATCH (p:Person)
RETURN collect(p.middleName) AS middleNames
// Only includes non-NULL values

// Include placeholder for NULLs
MATCH (p:Person)
RETURN collect(coalesce(p.middleName, 'N/A')) AS middleNames
```

---

## 8.9 Advanced Aggregation Patterns

### Nested Aggregations with WITH

```cypher
// Two-level aggregation
MATCH (c:Customer)-[:PLACED]->(o:Order)
WITH c, count(o) AS orderCount
WITH avg(orderCount) AS avgOrdersPerCustomer, 
     max(orderCount) AS maxOrders,
     count(c) AS totalCustomers
RETURN avgOrdersPerCustomer, maxOrders, totalCustomers
```

### Running Totals (Cumulative)

```cypher
// Cumulative sum using REDUCE
MATCH (s:Sale)
WHERE s.year = 2024
WITH s
ORDER BY s.month
WITH collect(s.amount) AS amounts
RETURN [i IN range(0, size(amounts)-1) | 
        reduce(total = 0, x IN amounts[0..i+1] | total + x)] AS runningTotal
```

### Aggregation by Time Periods

```cypher
// Group by date parts
MATCH (o:Order)
RETURN 
    o.orderDate.year AS year,
    o.orderDate.month AS month,
    count(o) AS orderCount,
    sum(o.total) AS monthlyRevenue
ORDER BY year, month

// Group by week
MATCH (o:Order)
RETURN 
    date.truncate('week', o.orderDate) AS week,
    count(o) AS orders
ORDER BY week
```

### Pivot-like Aggregation

```cypher
// Pivot by status
MATCH (o:Order)
RETURN 
    o.orderDate.month AS month,
    sum(CASE WHEN o.status = 'Completed' THEN o.total ELSE 0 END) AS completedRevenue,
    sum(CASE WHEN o.status = 'Pending' THEN o.total ELSE 0 END) AS pendingRevenue,
    sum(CASE WHEN o.status = 'Cancelled' THEN o.total ELSE 0 END) AS cancelledValue
ORDER BY month
```

### Top-N per Group

```cypher
// Top 3 products per category
MATCH (p:Product)-[:IN_CATEGORY]->(c:Category)
WITH c, p
ORDER BY p.sales DESC
WITH c, collect(p)[0..3] AS topProducts
RETURN c.name, [p IN topProducts | p.name] AS top3Products

// Alternative with subquery
MATCH (c:Category)
CALL {
    WITH c
    MATCH (c)<-[:IN_CATEGORY]-(p:Product)
    RETURN p
    ORDER BY p.sales DESC
    LIMIT 3
}
RETURN c.name, collect(p.name) AS topProducts
```

---

## 8.10 Python Examples

### Basic Aggregations

```python
from neo4j import GraphDatabase

URI = "neo4j://localhost:7687"
AUTH = ("neo4j", "password")

def run_aggregations(driver):
    with driver.session() as session:
        # Count and basic stats
        result = session.run("""
            MATCH (p:Product)
            RETURN 
                count(p) AS total,
                avg(p.price) AS avgPrice,
                min(p.price) AS minPrice,
                max(p.price) AS maxPrice,
                sum(p.price) AS totalValue
        """)
        stats = result.single()
        print(f"Total: {stats['total']}, Avg: {stats['avgPrice']:.2f}")
        
        # Grouped aggregation
        result = session.run("""
            MATCH (p:Product)
            RETURN p.category AS category, 
                   count(p) AS count,
                   avg(p.price) AS avgPrice
            ORDER BY count DESC
        """)
        for record in result:
            print(f"{record['category']}: {record['count']} products, ${record['avgPrice']:.2f} avg")

def collect_example(driver):
    with driver.session() as session:
        result = session.run("""
            MATCH (c:Customer)-[:PURCHASED]->(p:Product)
            WITH c, collect(p.name) AS products, sum(p.price) AS total
            WHERE size(products) >= 3
            RETURN c.name AS customer, products, total
            ORDER BY total DESC
            LIMIT 10
        """)
        for record in result:
            print(f"{record['customer']}: {record['products']} - ${record['total']}")

with GraphDatabase.driver(URI, auth=AUTH) as driver:
    run_aggregations(driver)
    collect_example(driver)
```

### Reporting with Aggregations

```python
def generate_sales_report(driver, year: int):
    with driver.session() as session:
        result = session.run("""
            MATCH (o:Order)
            WHERE o.orderDate.year = $year
            WITH o.orderDate.month AS month, 
                 count(o) AS orders,
                 sum(o.total) AS revenue
            ORDER BY month
            RETURN collect({month: month, orders: orders, revenue: revenue}) AS report
        """, year=year)
        
        report = result.single()['report']
        
        print(f"\n=== Sales Report {year} ===")
        print(f"{'Month':<10} {'Orders':<10} {'Revenue':<15}")
        print("-" * 35)
        
        total_orders = 0
        total_revenue = 0
        for row in report:
            print(f"{row['month']:<10} {row['orders']:<10} ${row['revenue']:,.2f}")
            total_orders += row['orders']
            total_revenue += row['revenue']
        
        print("-" * 35)
        print(f"{'Total':<10} {total_orders:<10} ${total_revenue:,.2f}")

with GraphDatabase.driver(URI, auth=AUTH) as driver:
    generate_sales_report(driver, 2024)
```

---

## Summary

### Key Takeaways

1. **Implicit Grouping**: Non-aggregated items become grouping keys automatically
2. **COUNT(*) vs COUNT(expr)**: `*` counts rows, expression counts non-NULL values
3. **COLLECT**: Creates lists from grouped data
4. **WITH + WHERE**: Cypher's equivalent to SQL HAVING clause
5. **NULL handling**: Aggregations generally ignore NULL values

### Quick Reference

```cypher
-- Basic aggregations
RETURN count(*), sum(n.val), avg(n.val), min(n.val), max(n.val)

-- Distinct count
RETURN count(DISTINCT n.prop)

-- Collect into list
RETURN collect(n.name), collect(DISTINCT n.name)

-- Statistical
RETURN stdev(n.val), percentileCont(n.val, 0.5)

-- Grouping
RETURN n.category, count(n)  // Implicit group by category

-- Filter aggregates (HAVING)
WITH n.category AS cat, count(n) AS cnt
WHERE cnt > 10
RETURN cat, cnt
```

---

## Exercises

### Exercise 8.1: Basic Aggregations
1. Count total customers, products, and orders in the database
2. Find the average order value and the total revenue
3. Find min and max product prices per category

### Exercise 8.2: COLLECT
1. For each customer, collect all product names they purchased
2. Create a list of all unique cities where employees work
3. Group products by category and collect their names sorted alphabetically

### Exercise 8.3: Complex Aggregations
1. Find customers whose average order value is above the global average
2. Identify the top 5 products by total quantity sold
3. Calculate month-over-month revenue growth rate

### Exercise 8.4: Statistical Analysis
1. Calculate the median salary per department
2. Find outlier orders (more than 2 standard deviations from mean)
3. Create salary percentile rankings for employees

---

**Next Chapter: [Chapter 9: Cypher - Working with Paths](09-cypher-paths.md)**
