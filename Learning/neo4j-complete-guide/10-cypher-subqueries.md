# Chapter 10: Cypher - Subqueries and UNION

## Learning Objectives
By the end of this chapter, you will:
- Use CALL subqueries for complex logic
- Apply EXISTS and COUNT subqueries for filtering
- Combine results with UNION and UNION ALL
- Understand correlated vs uncorrelated subqueries
- Use WITH for query composition

---

## 10.1 Introduction to Subqueries

### Why Subqueries?

Subqueries allow you to:
- Perform operations that can't be expressed in a single pattern
- Isolate computations with their own scope
- Create complex filtering conditions
- Combine multiple result sets

### Types of Subqueries

1. **CALL subqueries** - Full query blocks
2. **EXISTS subqueries** - Boolean existence checks
3. **COUNT subqueries** - Pattern counting
4. **Scalar subqueries** - Return single values

---

## 10.2 CALL Subqueries

### Basic CALL Syntax

```cypher
// Basic CALL subquery
CALL {
    MATCH (p:Person)
    WHERE p.age > 30
    RETURN p
    LIMIT 10
}
RETURN p.name, p.age
```

### Uncorrelated Subqueries

Uncorrelated subqueries don't reference outer scope variables:

```cypher
// Get average age (uncorrelated)
CALL {
    MATCH (p:Person)
    RETURN avg(p.age) AS avgAge
}
MATCH (person:Person)
WHERE person.age > avgAge
RETURN person.name, person.age, avgAge

// Find top products (uncorrelated)
CALL {
    MATCH (p:Product)
    RETURN p
    ORDER BY p.sales DESC
    LIMIT 5
}
RETURN p.name, p.sales AS topSellingProducts
```

### Correlated Subqueries

Correlated subqueries reference variables from outer scope:

```cypher
// Find each customer's most recent order
MATCH (c:Customer)
CALL {
    WITH c  // Pass outer variable into subquery
    MATCH (c)-[:PLACED]->(o:Order)
    RETURN o
    ORDER BY o.orderDate DESC
    LIMIT 1
}
RETURN c.name, o.orderDate AS lastOrderDate

// Get top 3 products per category
MATCH (cat:Category)
CALL {
    WITH cat
    MATCH (cat)<-[:IN_CATEGORY]-(p:Product)
    RETURN p
    ORDER BY p.sales DESC
    LIMIT 3
}
RETURN cat.name, collect(p.name) AS topProducts
```

### Subqueries with Aggregation

```cypher
// Calculate running stats
MATCH (c:Customer)
CALL {
    WITH c
    MATCH (c)-[:PLACED]->(o:Order)
    RETURN count(o) AS orderCount, sum(o.total) AS totalSpent
}
RETURN c.name, orderCount, totalSpent
ORDER BY totalSpent DESC

// Complex metric calculation
MATCH (p:Product)
CALL {
    WITH p
    MATCH (p)<-[r:REVIEWED]-()
    RETURN avg(r.rating) AS avgRating, count(r) AS reviewCount
}
WHERE reviewCount >= 5
RETURN p.name, avgRating, reviewCount
ORDER BY avgRating DESC
```

---

## 10.3 EXISTS Subqueries

### Basic EXISTS

```cypher
// Check if pattern exists
MATCH (p:Person)
WHERE EXISTS {
    (p)-[:WORKS_FOR]->(:Company {name: 'Google'})
}
RETURN p.name AS googleEmployee

// Negate existence
MATCH (p:Person)
WHERE NOT EXISTS {
    (p)-[:WORKS_FOR]->()
}
RETURN p.name AS unemployed
```

### EXISTS with Complex Patterns

```cypher
// Multiple conditions in EXISTS
MATCH (p:Person)
WHERE EXISTS {
    MATCH (p)-[:KNOWS]->(friend:Person)-[:WORKS_FOR]->(c:Company)
    WHERE c.industry = 'Technology'
}
RETURN p.name AS knowsTechWorker

// Nested patterns
MATCH (c:Customer)
WHERE EXISTS {
    MATCH (c)-[:PLACED]->(o:Order)-[:CONTAINS]->(p:Product)
    WHERE p.price > 1000
}
RETURN c.name AS premiumBuyer
```

### EXISTS with WHERE Clause

```cypher
// Filter inside EXISTS
MATCH (p:Person)
WHERE EXISTS {
    MATCH (p)-[:PURCHASED]->(product:Product)
    WHERE product.category = 'Electronics'
      AND product.price > 500
}
RETURN p.name

// Date-based existence
MATCH (c:Customer)
WHERE EXISTS {
    MATCH (c)-[:PLACED]->(o:Order)
    WHERE o.orderDate >= date() - duration('P30D')
}
RETURN c.name AS recentCustomer
```

### Combining EXISTS Clauses

```cypher
// AND logic
MATCH (p:Person)
WHERE EXISTS { (p)-[:WORKS_FOR]->(:Company) }
  AND EXISTS { (p)-[:HAS_SKILL]->(:Skill {name: 'Python'}) }
RETURN p.name AS employedPythonDev

// OR logic
MATCH (p:Person)
WHERE EXISTS { (p)-[:KNOWS]->(:Celebrity) }
   OR EXISTS { (p)-[:WORKS_FOR]->(:Company {fortune500: true}) }
RETURN p.name AS wellConnected
```

---

## 10.4 COUNT Subqueries

### Basic COUNT Subquery

```cypher
// Count pattern occurrences
MATCH (p:Person)
WHERE COUNT {
    (p)-[:KNOWS]->(:Person)
} >= 5
RETURN p.name AS popular

// Exact count check
MATCH (c:Customer)
WHERE COUNT {
    (c)-[:PLACED]->(:Order)
} = 1
RETURN c.name AS oneTimeCustomer
```

### COUNT vs EXISTS

```cypher
// EXISTS is more efficient for boolean check
// ✅ Use EXISTS for "at least one"
WHERE EXISTS { (p)-[:KNOWS]->() }

// ✅ Use COUNT for specific numbers
WHERE COUNT { (p)-[:KNOWS]->() } >= 5

// ❌ Don't use COUNT just to check existence
WHERE COUNT { (p)-[:KNOWS]->() } > 0  // Use EXISTS instead
```

### COUNT with Conditions

```cypher
// Filtered count
MATCH (p:Person)
WHERE COUNT {
    (p)-[:PURCHASED]->(product:Product)
    WHERE product.price > 100
} >= 3
RETURN p.name AS frequentBigSpender

// Multiple count conditions
MATCH (p:Product)
WHERE COUNT { (p)<-[:REVIEWED {rating: 5}]-() } > 10
  AND COUNT { (p)<-[:REVIEWED {rating: 1}]-() } < 3
RETURN p.name AS highlyRated
```

---

## 10.5 Scalar Subqueries

### Return Single Value

```cypher
// Compare against computed value
MATCH (e:Employee)
WHERE e.salary > (
    CALL {
        MATCH (emp:Employee)
        RETURN avg(emp.salary) AS avgSalary
    }
    RETURN avgSalary
)
RETURN e.name, e.salary AS aboveAverageSalary

// Use scalar in calculations
MATCH (p:Product)
RETURN p.name,
       p.price,
       p.price / (
           CALL {
               MATCH (prod:Product)
               RETURN max(prod.price) AS maxPrice
           }
           RETURN maxPrice
       ) AS priceRatio
```

---

## 10.6 UNION and UNION ALL

### Basic UNION

```cypher
// Combine results (removes duplicates)
MATCH (p:Person)-[:LIVES_IN]->(:City {name: 'NYC'})
RETURN p.name AS name, 'NYC' AS city
UNION
MATCH (p:Person)-[:LIVES_IN]->(:City {name: 'LA'})
RETURN p.name AS name, 'LA' AS city
```

### UNION ALL

```cypher
// Combine results (keeps duplicates)
MATCH (p:Person)-[:LIKES]->(m:Movie)
RETURN m.title AS title, 'like' AS interaction
UNION ALL
MATCH (p:Person)-[:WATCHED]->(m:Movie)
RETURN m.title AS title, 'watch' AS interaction
// Same movie can appear multiple times
```

### UNION Column Requirements

```cypher
// All UNION parts must have same column names and count
-- ✅ Correct
MATCH (p:Person) RETURN p.name AS name, 'Person' AS type
UNION
MATCH (c:Company) RETURN c.name AS name, 'Company' AS type

-- ❌ Wrong - different column names
MATCH (p:Person) RETURN p.name AS personName
UNION
MATCH (c:Company) RETURN c.name AS companyName  -- Error!

-- ❌ Wrong - different column count
MATCH (p:Person) RETURN p.name, p.age
UNION
MATCH (c:Company) RETURN c.name  -- Error!
```

### Complex UNION Patterns

```cypher
// Multiple UNION clauses
MATCH (e:Employee)
RETURN e.name AS name, 'Employee' AS type, e.salary AS value
UNION ALL
MATCH (c:Contractor)
RETURN c.name AS name, 'Contractor' AS type, c.rate * 160 AS value
UNION ALL
MATCH (i:Intern)
RETURN i.name AS name, 'Intern' AS type, i.stipend AS value
ORDER BY value DESC

// Post-UNION processing
CALL {
    MATCH (p:Person)-[:LIKES]->(item)
    RETURN p.name AS name, labels(item)[0] AS itemType
    UNION ALL
    MATCH (p:Person)-[:OWNS]->(item)
    RETURN p.name AS name, labels(item)[0] AS itemType
}
WITH name, collect(DISTINCT itemType) AS interests
RETURN name, interests
```

---

## 10.7 WITH for Query Composition

### Basic WITH Usage

```cypher
// Chain query stages
MATCH (p:Person)
WHERE p.age > 25
WITH p
MATCH (p)-[:WORKS_FOR]->(c:Company)
WITH p, c
WHERE c.size > 100
RETURN p.name, c.name
```

### WITH for Variable Scope Control

```cypher
// Only pass needed variables
MATCH (c:Customer)-[:PLACED]->(o:Order)
WITH c, sum(o.total) AS totalSpent  // o is no longer accessible
WHERE totalSpent > 1000
MATCH (c)-[:LIVES_IN]->(city:City)
RETURN c.name, totalSpent, city.name

// Reset scope completely
MATCH (p:Person)
WITH count(p) AS personCount
MATCH (c:Company)
RETURN personCount, count(c) AS companyCount
```

### WITH for Ordering Before Operations

```cypher
// Order before collect
MATCH (c:Category)<-[:IN_CATEGORY]-(p:Product)
WITH c, p
ORDER BY p.name
WITH c, collect(p.name) AS products
RETURN c.name, products

// Order before limit in subquery
MATCH (customer:Customer)
WITH customer
ORDER BY customer.name
LIMIT 10
MATCH (customer)-[:PLACED]->(o:Order)
RETURN customer.name, count(o) AS orders
```

---

## 10.8 Practical Subquery Patterns

### Top-N Per Group

```cypher
// Top 3 products per category
MATCH (c:Category)
CALL {
    WITH c
    MATCH (c)<-[:IN_CATEGORY]-(p:Product)
    RETURN p
    ORDER BY p.sales DESC
    LIMIT 3
}
RETURN c.name AS category, collect(p.name) AS topProducts
```

### Conditional Data Retrieval

```cypher
// Get extra data only if condition met
MATCH (c:Customer)
CALL {
    WITH c
    OPTIONAL MATCH (c)-[:PLACED]->(o:Order)
    WHERE o.total > 500
    RETURN collect(o) AS bigOrders
}
WITH c, bigOrders
WHERE size(bigOrders) > 0
RETURN c.name, size(bigOrders) AS bigOrderCount
```

### Running Totals / Window-like Functions

```cypher
// Running total simulation
MATCH (o:Order)
WHERE o.orderDate.year = 2024
WITH o
ORDER BY o.orderDate
WITH collect({date: o.orderDate, amount: o.total}) AS orders
UNWIND range(0, size(orders)-1) AS i
WITH orders[i] AS current,
     reduce(sum = 0, j IN range(0, i) | sum + orders[j].amount) AS runningTotal
RETURN current.date, current.amount, runningTotal
```

### Pivot Data

```cypher
// Pivot order counts by month
MATCH (o:Order)
WHERE o.orderDate.year = 2024
WITH o.orderDate.month AS month, count(o) AS orders
ORDER BY month
WITH collect({month: month, orders: orders}) AS monthlyData
RETURN 
    [m IN monthlyData WHERE m.month = 1 | m.orders][0] AS Jan,
    [m IN monthlyData WHERE m.month = 2 | m.orders][0] AS Feb,
    [m IN monthlyData WHERE m.month = 3 | m.orders][0] AS Mar
    // ... continue for all months
```

### Finding Missing Relationships

```cypher
// Products without reviews
MATCH (p:Product)
WHERE NOT EXISTS {
    (p)<-[:REVIEWED]-()
}
RETURN p.name AS unreviewed

// Customers who haven't ordered recently
MATCH (c:Customer)
WHERE EXISTS { (c)-[:PLACED]->() }  // Has ordered before
  AND NOT EXISTS {
    MATCH (c)-[:PLACED]->(o:Order)
    WHERE o.orderDate >= date() - duration('P90D')
}
RETURN c.name AS inactiveCustomer
```

---

## 10.9 Performance Considerations

### Subquery Execution

```cypher
// ❌ Subquery runs for every outer row
MATCH (c:Customer)
CALL {
    WITH c
    MATCH (c)-[:PLACED]->(o:Order)
    RETURN sum(o.total) AS total
}
RETURN c.name, total

// ✅ Often more efficient with direct pattern
MATCH (c:Customer)-[:PLACED]->(o:Order)
WITH c, sum(o.total) AS total
RETURN c.name, total
```

### EXISTS vs Pattern Matching

```cypher
// ✅ EXISTS is optimized to stop at first match
WHERE EXISTS { (p)-[:KNOWS]->(:Celebrity) }

// ❌ Less efficient - finds all matches then checks
WHERE (p)-[:KNOWS]->(:Celebrity)  // Old syntax, same result but may be slower
```

### UNION vs CALL with Conditional Logic

```cypher
// UNION approach
MATCH (n:Person) RETURN n.name AS name
UNION
MATCH (n:Company) RETURN n.name AS name

// Alternative with CALL (sometimes more flexible)
CALL {
    MATCH (n:Person) RETURN n.name AS name, 'Person' AS type
    UNION ALL
    MATCH (n:Company) RETURN n.name AS name, 'Company' AS type
}
WITH name, type
ORDER BY name
RETURN name, type
```

---

## 10.10 Python Examples

### Working with Subqueries

```python
from neo4j import GraphDatabase

URI = "neo4j://localhost:7687"
AUTH = ("neo4j", "password")

def get_customers_above_average(driver):
    """Find customers who spend above average."""
    with driver.session() as session:
        result = session.run("""
            CALL {
                MATCH (c:Customer)-[:PLACED]->(o:Order)
                RETURN avg(o.total) AS avgOrderValue
            }
            MATCH (customer:Customer)-[:PLACED]->(order:Order)
            WITH customer, avg(order.total) AS customerAvg, avgOrderValue
            WHERE customerAvg > avgOrderValue
            RETURN customer.name AS name, 
                   customerAvg AS avgSpend,
                   avgOrderValue AS globalAvg
            ORDER BY avgSpend DESC
        """)
        
        print("Customers above average spending:")
        for record in result:
            print(f"  {record['name']}: ${record['avgSpend']:.2f} (avg: ${record['globalAvg']:.2f})")

def get_top_products_per_category(driver, limit: int = 3):
    """Get top N products for each category."""
    with driver.session() as session:
        result = session.run("""
            MATCH (cat:Category)
            CALL {
                WITH cat
                MATCH (cat)<-[:IN_CATEGORY]-(p:Product)
                RETURN p
                ORDER BY p.sales DESC
                LIMIT $limit
            }
            RETURN cat.name AS category, 
                   collect({name: p.name, sales: p.sales}) AS products
        """, limit=limit)
        
        print(f"\nTop {limit} products per category:")
        for record in result:
            print(f"\n{record['category']}:")
            for product in record['products']:
                print(f"  - {product['name']}: {product['sales']} sales")

def search_multiple_types(driver, search_term: str):
    """Search across multiple entity types using UNION."""
    with driver.session() as session:
        result = session.run("""
            CALL {
                MATCH (p:Person)
                WHERE p.name CONTAINS $term
                RETURN p.name AS name, 'Person' AS type, p.email AS detail
                UNION ALL
                MATCH (c:Company)
                WHERE c.name CONTAINS $term
                RETURN c.name AS name, 'Company' AS type, c.website AS detail
                UNION ALL
                MATCH (pr:Product)
                WHERE pr.name CONTAINS $term
                RETURN pr.name AS name, 'Product' AS type, toString(pr.price) AS detail
            }
            RETURN name, type, detail
            ORDER BY type, name
        """, term=search_term)
        
        print(f"\nSearch results for '{search_term}':")
        current_type = None
        for record in result:
            if record['type'] != current_type:
                current_type = record['type']
                print(f"\n{current_type}s:")
            print(f"  - {record['name']}: {record['detail']}")

with GraphDatabase.driver(URI, auth=AUTH) as driver:
    get_customers_above_average(driver)
    get_top_products_per_category(driver)
    search_multiple_types(driver, "tech")
```

---

## Summary

### Key Takeaways

1. **CALL subqueries**: Isolate complex logic, support correlated queries
2. **EXISTS**: Efficient boolean existence checks
3. **COUNT**: Count pattern occurrences for filtering
4. **UNION/UNION ALL**: Combine result sets (UNION removes duplicates)
5. **WITH**: Control variable scope and chain query stages

### Quick Reference

```cypher
-- CALL subquery (correlated)
MATCH (c:Customer)
CALL {
    WITH c
    MATCH (c)-[:PLACED]->(o:Order)
    RETURN count(o) AS orderCount
}
RETURN c.name, orderCount

-- EXISTS subquery
WHERE EXISTS { (p)-[:KNOWS]->(:Celebrity) }
WHERE NOT EXISTS { (p)-[:WORKS_FOR]->() }

-- COUNT subquery
WHERE COUNT { (p)-[:KNOWS]->() } >= 5

-- UNION (removes duplicates)
RETURN ... UNION RETURN ...

-- UNION ALL (keeps all)
RETURN ... UNION ALL RETURN ...
```

---

## Exercises

### Exercise 10.1: CALL Subqueries
1. Find each customer's most expensive single order
2. Get top 5 employees per department by salary
3. Calculate each product's sales rank within its category

### Exercise 10.2: EXISTS and COUNT
1. Find people who work at a company but don't know anyone at that company
2. Find products with at least 10 reviews and average rating above 4
3. Identify customers who have bought from all categories

### Exercise 10.3: UNION
1. Combine employees and contractors into a single list
2. Create a unified search across people, products, and companies
3. Merge multiple relationship types into a single "interaction" list

### Exercise 10.4: Complex Queries
1. Find the employee with the highest salary in each department
2. Identify circular references in a dependency graph
3. Calculate month-over-month growth using subqueries

---

**Next Chapter: [Chapter 11: Cypher - Functions](11-cypher-functions.md)**
