# Chapter 19: Query Optimization

## Learning Objectives
By the end of this chapter, you will:
- Analyze query execution with EXPLAIN and PROFILE
- Identify and fix common performance issues
- Write efficient Cypher patterns
- Optimize traversal operations
- Implement query performance best practices

---

## 19.1 Understanding Query Execution

### The Query Pipeline

```
Cypher Query → Parser → Planner → Optimizer → Executor → Results
```

1. **Parser**: Validates syntax
2. **Planner**: Creates execution plan
3. **Optimizer**: Improves plan efficiency
4. **Executor**: Runs the plan

### EXPLAIN vs PROFILE

```cypher
// EXPLAIN: Shows plan WITHOUT executing
EXPLAIN MATCH (p:Person)-[:KNOWS]->(friend)
WHERE p.name = 'Alice'
RETURN friend.name

// PROFILE: Executes and shows actual statistics
PROFILE MATCH (p:Person)-[:KNOWS]->(friend)
WHERE p.name = 'Alice'
RETURN friend.name
```

---

## 19.2 Reading Execution Plans

### Plan Operators

```cypher
PROFILE
MATCH (p:Person {email: 'alice@example.com'})-[:PURCHASED]->(o:Order)
RETURN p.name, o.id
```

Key operators to understand:

| Operator | Meaning | Performance |
|----------|---------|-------------|
| `NodeIndexSeek` | Index lookup | ✅ Fast |
| `NodeUniqueIndexSeek` | Unique constraint index | ✅ Fast |
| `DirectedRelationshipIndexSeek` | Relationship index | ✅ Fast |
| `NodeByLabelScan` | Scan all nodes with label | ⚠️ Slow for large datasets |
| `AllNodesScan` | Scan entire database | ❌ Very slow |
| `Filter` | Filter rows | Depends on position |
| `Expand(All)` | Traverse relationships | Normal |
| `Eager` | Materialization barrier | ⚠️ Memory intensive |

### Reading Plan Output

```
+------------------------+----------------+------+---------+----------------+
| Operator               | Estimated Rows | Rows | DB Hits | Memory (Bytes) |
+------------------------+----------------+------+---------+----------------+
| +ProduceResults        |             10 |   10 |       0 |                |
| |                      +----------------+------+---------+----------------+
| +Projection            |             10 |   10 |      20 |                |
| |                      +----------------+------+---------+----------------+
| +Expand(All)           |             10 |   10 |      20 |                |
| |                      +----------------+------+---------+----------------+
| +NodeIndexSeek         |              1 |    1 |       2 |            120 |
+------------------------+----------------+------+---------+----------------+
```

**Key Metrics:**
- **Estimated Rows**: Planner's prediction
- **Rows**: Actual rows processed
- **DB Hits**: Database operations (lower is better)
- **Memory**: Memory consumed

---

## 19.3 Optimization Techniques

### 1. Use Indexes Effectively

```cypher
// ❌ Without index: Full label scan
MATCH (p:Product)
WHERE p.name = 'Laptop'
RETURN p

// ✅ With index: Direct lookup
CREATE INDEX product_name FOR (p:Product) ON (p.name)
// Same query now uses index

// ❌ Index not used (function on indexed property)
MATCH (p:Person)
WHERE toLower(p.email) = 'alice@example.com'
RETURN p

// ✅ Store normalized data
MATCH (p:Person)
WHERE p.emailLower = 'alice@example.com'
RETURN p
```

### 2. Filter Early

```cypher
// ❌ Filter late: Processes many rows
MATCH (c:Customer)-[:PURCHASED]->(o:Order)-[:CONTAINS]->(p:Product)
WHERE c.country = 'USA'
RETURN c, o, p

// ✅ Filter early: Reduces rows immediately
MATCH (c:Customer)
WHERE c.country = 'USA'
MATCH (c)-[:PURCHASED]->(o:Order)-[:CONTAINS]->(p:Product)
RETURN c, o, p

// Even better with index
CREATE INDEX customer_country FOR (c:Customer) ON (c.country)
```

### 3. Limit Traversal Depth

```cypher
// ❌ Unlimited depth can explode
MATCH path = (a:Person)-[:KNOWS*]->(b:Person)
RETURN path

// ✅ Always limit variable-length paths
MATCH path = (a:Person)-[:KNOWS*1..5]->(b:Person)
RETURN path

// ✅ Use shortest path for point-to-point
MATCH path = shortestPath((a:Person)-[:KNOWS*]->(b:Person))
WHERE a.name = 'Alice' AND b.name = 'Bob'
RETURN path
```

### 4. Avoid Cartesian Products

```cypher
// ❌ Cartesian product (multiplies all rows)
MATCH (p:Product), (c:Category)
WHERE p.category = c.name
RETURN p, c

// ✅ Use relationship instead
MATCH (p:Product)-[:IN_CATEGORY]->(c:Category)
RETURN p, c

// If no relationship, at least filter one side first
MATCH (c:Category {name: 'Electronics'})
MATCH (p:Product)
WHERE p.category = c.name
RETURN p, c
```

### 5. Use OPTIONAL MATCH Carefully

```cypher
// ❌ OPTIONAL MATCH before filtering
MATCH (c:Customer)
OPTIONAL MATCH (c)-[:PURCHASED]->(o:Order)
WHERE o.total > 100
RETURN c, o

// ✅ Filter in OPTIONAL MATCH
MATCH (c:Customer)
OPTIONAL MATCH (c)-[:PURCHASED]->(o:Order)
WHERE o.total > 100
RETURN c, o

// ✅ Or use pattern comprehension
MATCH (c:Customer)
RETURN c, [(c)-[:PURCHASED]->(o:Order) WHERE o.total > 100 | o] AS highValueOrders
```

---

## 19.4 Pattern Optimization

### Relationship Type Specificity

```cypher
// ❌ Query all relationship types
MATCH (a:Person)-[r]->(b)
RETURN type(r), count(*)

// ✅ Specify relationship types
MATCH (a:Person)-[r:KNOWS|WORKS_WITH]->(b)
RETURN type(r), count(*)
```

### Direction Matters

```cypher
// ✅ Use direction when known
MATCH (a:Person)-[:KNOWS]->(b:Person)  // Directed, more efficient
RETURN a, b

// ⚠️ Undirected doubles the work
MATCH (a:Person)-[:KNOWS]-(b:Person)  // Checks both directions
RETURN a, b
```

### Pattern vs Multiple MATCH

```cypher
// Single pattern (usually better)
MATCH (a:Person)-[:KNOWS]->(b:Person)-[:LIVES_IN]->(c:City)
WHERE a.name = 'Alice'
RETURN b.name, c.name

// Multiple MATCH (sometimes needed for complex logic)
MATCH (a:Person {name: 'Alice'})-[:KNOWS]->(b:Person)
MATCH (b)-[:LIVES_IN]->(c:City)
RETURN b.name, c.name
```

---

## 19.5 Aggregation Optimization

### Push Down Aggregation

```cypher
// ❌ Aggregate late
MATCH (c:Customer)-[:PURCHASED]->(o:Order)-[:CONTAINS]->(p:Product)
RETURN c.name, sum(o.total) AS totalSpent
// Processes all products unnecessarily

// ✅ Aggregate early
MATCH (c:Customer)-[:PURCHASED]->(o:Order)
WITH c, sum(o.total) AS totalSpent
RETURN c.name, totalSpent
```

### Use count(DISTINCT) Carefully

```cypher
// ❌ Expensive distinct
MATCH (c:Customer)-[:PURCHASED]->(o:Order)-[:CONTAINS]->(p:Product)
RETURN c.name, count(DISTINCT p) AS productCount

// ✅ Aggregate at appropriate level
MATCH (c:Customer)-[:PURCHASED]->(o:Order)
WITH c, o
MATCH (o)-[:CONTAINS]->(p:Product)
WITH c, collect(DISTINCT p) AS products
RETURN c.name, size(products) AS productCount
```

---

## 19.6 Subquery Optimization

### EXISTS for Filtering

```cypher
// ✅ EXISTS subquery (efficient for existence check)
MATCH (c:Customer)
WHERE EXISTS {
    MATCH (c)-[:PURCHASED]->(o:Order)
    WHERE o.total > 1000
}
RETURN c.name

// ❌ Less efficient
MATCH (c:Customer)-[:PURCHASED]->(o:Order)
WHERE o.total > 1000
RETURN DISTINCT c.name
```

### CALL Subquery for Complex Logic

```cypher
// Process in batches with subquery
MATCH (c:Customer)
CALL {
    WITH c
    MATCH (c)-[:PURCHASED]->(o:Order)
    RETURN sum(o.total) AS total, count(o) AS orderCount
}
RETURN c.name, total, orderCount
```

---

## 19.7 Write Query Optimization

### Batch Processing

```cypher
// ❌ One at a time
UNWIND $items AS item
CREATE (p:Product {name: item.name, price: item.price})

// ✅ Use CALL IN TRANSACTIONS for large batches
CALL {
    UNWIND $items AS item
    CREATE (p:Product {name: item.name, price: item.price})
} IN TRANSACTIONS OF 1000 ROWS
```

### MERGE Optimization

```cypher
// ❌ MERGE without index is slow
MERGE (c:Customer {email: $email})
ON CREATE SET c.name = $name

// ✅ Create constraint/index first
CREATE CONSTRAINT customer_email FOR (c:Customer) REQUIRE c.email IS UNIQUE
// Now MERGE uses index

// ❌ MERGE full pattern is expensive
MERGE (a:Person {name: 'Alice'})-[:KNOWS]->(b:Person {name: 'Bob'})

// ✅ MERGE nodes separately, then relationship
MERGE (a:Person {name: 'Alice'})
MERGE (b:Person {name: 'Bob'})
MERGE (a)-[:KNOWS]->(b)
```

---

## 19.8 Memory Optimization

### Avoid Eager Operations

```cypher
// Operations that cause Eager:
// - COLLECT after UNWIND
// - ORDER BY before write operations
// - Some aggregations

// Check for Eager in plan
PROFILE
MATCH (p:Person)-[:KNOWS]->(friend)
WITH collect(friend) AS friends
UNWIND friends AS f
RETURN f.name
```

### Limit Memory with Streaming

```cypher
// ❌ Collect everything in memory
MATCH (p:Product)
WITH collect(p) AS allProducts
RETURN size(allProducts)

// ✅ Stream and count
MATCH (p:Product)
RETURN count(p)
```

### Use SKIP/LIMIT for Pagination

```cypher
// ✅ Efficient pagination
MATCH (p:Product)
WHERE p.category = 'Electronics'
RETURN p
ORDER BY p.name
SKIP $offset
LIMIT $pageSize
```

---

## 19.9 Query Hints

### Index Hints

```cypher
// Force index usage
MATCH (p:Person)
USING INDEX p:Person(email)
WHERE p.email = $email
RETURN p

// Force specific index when multiple exist
MATCH (p:Person)
USING INDEX p:Person(name)
WHERE p.name = 'Alice' AND p.email IS NOT NULL
RETURN p
```

### Scan Hints

```cypher
// Force label scan (rarely needed)
MATCH (p:Person)
USING SCAN p:Person
WHERE p.age > 30
RETURN p
```

### Join Hints

```cypher
// Force join order
MATCH (a:Person), (b:Person)
USING JOIN ON a
WHERE a.name = 'Alice' AND (a)-[:KNOWS]->(b)
RETURN b
```

---

## 19.10 Monitoring and Diagnostics

### Query Logging

```cypher
// Enable query logging in neo4j.conf:
// db.logs.query.enabled=true
// db.logs.query.threshold=1000ms

// View slow queries
CALL dbms.listQueries() YIELD queryId, query, elapsedTimeMillis
WHERE elapsedTimeMillis > 1000
RETURN queryId, query, elapsedTimeMillis
```

### Query Statistics

```cypher
// Get database statistics
CALL db.stats.retrieve('GRAPH COUNTS')

// Index statistics
CALL db.stats.retrieve('INDEX USAGE')
```

### Python Monitoring Example

```python
from neo4j import GraphDatabase
import time

URI = "neo4j://localhost:7687"
AUTH = ("neo4j", "password")

class QueryAnalyzer:
    def __init__(self, uri, auth):
        self.driver = GraphDatabase.driver(uri, auth=auth)
    
    def close(self):
        self.driver.close()
    
    def profile_query(self, query: str, params: dict = None):
        """Profile a query and return performance metrics."""
        with self.driver.session() as session:
            start_time = time.time()
            
            # Run with PROFILE
            profile_query = f"PROFILE {query}"
            result = session.run(profile_query, params or {})
            
            # Consume all results
            records = list(result)
            
            # Get summary
            summary = result.consume()
            elapsed = time.time() - start_time
            
            # Extract plan details
            plan = summary.profile
            
            return {
                'elapsed_seconds': elapsed,
                'db_hits': self._total_db_hits(plan),
                'rows_processed': plan.db_hits if plan else 0,
                'operators': self._extract_operators(plan),
                'result_count': len(records)
            }
    
    def _total_db_hits(self, plan, total=0):
        """Recursively sum DB hits."""
        if plan is None:
            return total
        total += plan.db_hits
        for child in plan.children:
            total = self._total_db_hits(child, total)
        return total
    
    def _extract_operators(self, plan, operators=None):
        """Extract all operators from plan."""
        if operators is None:
            operators = []
        if plan is None:
            return operators
        
        operators.append({
            'operator': plan.operator_type,
            'db_hits': plan.db_hits,
            'rows': plan.rows
        })
        
        for child in plan.children:
            self._extract_operators(child, operators)
        return operators
    
    def compare_queries(self, query1: str, query2: str, params: dict = None):
        """Compare performance of two queries."""
        print("Analyzing Query 1...")
        result1 = self.profile_query(query1, params)
        
        print("Analyzing Query 2...")
        result2 = self.profile_query(query2, params)
        
        print("\n=== Query Comparison ===")
        print(f"{'Metric':<20} {'Query 1':>15} {'Query 2':>15} {'Diff':>15}")
        print("-" * 65)
        
        for metric in ['elapsed_seconds', 'db_hits', 'result_count']:
            v1 = result1[metric]
            v2 = result2[metric]
            diff = v2 - v1
            diff_str = f"{diff:+.2f}" if isinstance(diff, float) else f"{diff:+d}"
            print(f"{metric:<20} {v1:>15.4f} {v2:>15.4f} {diff_str:>15}")
        
        return result1, result2
    
    def suggest_indexes(self, query: str):
        """Analyze query and suggest indexes."""
        with self.driver.session() as session:
            result = session.run(f"EXPLAIN {query}")
            plan = result.consume().plan
            
            suggestions = []
            self._find_scans(plan, suggestions)
            
            return suggestions
    
    def _find_scans(self, plan, suggestions):
        """Find label scans that could benefit from indexes."""
        if plan is None:
            return
        
        if 'Scan' in plan.operator_type:
            args = plan.arguments
            label = args.get('LabelName', args.get('label', 'Unknown'))
            suggestions.append({
                'operator': plan.operator_type,
                'label': label,
                'suggestion': f"Consider adding an index on :{label} for filtered properties"
            })
        
        for child in plan.children:
            self._find_scans(child, suggestions)

# Usage
analyzer = QueryAnalyzer(URI, AUTH)
try:
    # Profile a query
    metrics = analyzer.profile_query("""
        MATCH (c:Customer)-[:PURCHASED]->(o:Order)
        WHERE c.country = 'USA'
        RETURN c.name, sum(o.total) AS totalSpent
    """)
    
    print(f"Query completed in {metrics['elapsed_seconds']:.3f}s")
    print(f"Total DB hits: {metrics['db_hits']}")
    
    # Get index suggestions
    suggestions = analyzer.suggest_indexes("""
        MATCH (p:Product)
        WHERE p.category = 'Electronics' AND p.price > 100
        RETURN p
    """)
    
    for s in suggestions:
        print(f"Suggestion: {s['suggestion']}")
        
finally:
    analyzer.close()
```

---

## Summary

### Optimization Checklist

1. ✅ Use indexes for frequently queried properties
2. ✅ Filter early in queries
3. ✅ Limit variable-length path depth
4. ✅ Avoid Cartesian products
5. ✅ Specify relationship types and directions
6. ✅ Use PROFILE to analyze actual performance
7. ✅ Batch large write operations
8. ✅ MERGE nodes separately, then relationships

### Key Commands

```cypher
-- Analyze queries
EXPLAIN <query>
PROFILE <query>

-- Index hints
USING INDEX n:Label(property)
USING SCAN n:Label

-- Batch writes
CALL { ... } IN TRANSACTIONS OF 1000 ROWS
```

---

## Exercises

### Exercise 19.1: Query Analysis
1. Write a query to find customers with their order totals
2. Use PROFILE to analyze the query
3. Identify any NodeByLabelScan operations
4. Add indexes and re-analyze

### Exercise 19.2: Optimization Challenge
Optimize this query:
```cypher
MATCH (c:Customer), (p:Product)
WHERE (c)-[:PURCHASED]->(:Order)-[:CONTAINS]->(p)
  AND c.country = 'USA'
  AND p.category = 'Electronics'
RETURN c.name, collect(p.name) AS products
```

### Exercise 19.3: Large Dataset
1. Create 100,000 nodes with varying properties
2. Write queries with and without indexes
3. Measure and compare performance

### Exercise 19.4: Write Optimization
1. Write a batch import for 10,000 products
2. Optimize using CALL IN TRANSACTIONS
3. Compare import times

---

**Next Chapter: [Chapter 20: Importing Data](20-importing-data.md)**
