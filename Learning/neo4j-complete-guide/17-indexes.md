# Chapter 17: Indexes

## Learning Objectives
By the end of this chapter, you will:
- Understand different index types in Neo4j
- Create and manage indexes effectively
- Use indexes for optimal query performance
- Implement full-text search indexes
- Apply indexing best practices

---

## 17.1 Understanding Indexes

### Why Indexes Matter

Without indexes, Neo4j must scan all nodes with a given label to find matches:

```cypher
// Without index: Full scan of all Person nodes
MATCH (p:Person {email: 'alice@example.com'})
RETURN p

// With index: Direct lookup
CREATE INDEX person_email FOR (p:Person) ON (p.email)
// Now the same query uses the index
```

### Index Types in Neo4j

| Type | Use Case | Lookup Type |
|------|----------|-------------|
| **Range Index** | Equality, range, prefix, existence | B+ tree |
| **Text Index** | String equality, prefix, suffix, contains | Trigram-based |
| **Point Index** | Spatial queries, distance | R-tree |
| **Full-Text Index** | Natural language search | Lucene |
| **Token Lookup Index** | Label/type lookups | Internal |

---

## 17.2 Range Indexes

### Creating Range Indexes

```cypher
// Single property index
CREATE INDEX person_email FOR (p:Person) ON (p.email)

// Index with explicit name
CREATE INDEX idx_product_sku FOR (p:Product) ON (p.sku)

// Composite index (multiple properties)
CREATE INDEX person_name_city FOR (p:Person) ON (p.firstName, p.lastName, p.city)

// Relationship property index
CREATE INDEX knows_since FOR ()-[r:KNOWS]-() ON (r.since)
```

### Range Index Operations

Range indexes support:

```cypher
// Equality
MATCH (p:Person) WHERE p.email = 'alice@example.com' RETURN p

// Range queries
MATCH (p:Product) WHERE p.price > 100 AND p.price < 500 RETURN p

// Prefix matching (strings)
MATCH (p:Person) WHERE p.name STARTS WITH 'Ali' RETURN p

// Existence check
MATCH (p:Person) WHERE p.email IS NOT NULL RETURN p

// IN list
MATCH (p:Person) WHERE p.status IN ['active', 'pending'] RETURN p
```

### Composite Index Usage

```cypher
// Create composite index
CREATE INDEX person_location FOR (p:Person) ON (p.country, p.city)

// ✅ Uses index (left-to-right)
MATCH (p:Person) WHERE p.country = 'USA' RETURN p
MATCH (p:Person) WHERE p.country = 'USA' AND p.city = 'NYC' RETURN p

// ❌ Cannot use index (skips first property)
MATCH (p:Person) WHERE p.city = 'NYC' RETURN p
```

---

## 17.3 Text Indexes

### Creating Text Indexes

```cypher
// Text index for string operations
CREATE TEXT INDEX product_name_text FOR (p:Product) ON (p.name)

// Text index on relationship
CREATE TEXT INDEX review_content FOR ()-[r:REVIEWED]-() ON (r.content)
```

### Text Index Operations

```cypher
// Equality
MATCH (p:Product) WHERE p.name = 'MacBook Pro' RETURN p

// STARTS WITH
MATCH (p:Product) WHERE p.name STARTS WITH 'Mac' RETURN p

// ENDS WITH (text index required)
MATCH (p:Product) WHERE p.name ENDS WITH 'Pro' RETURN p

// CONTAINS (text index required)
MATCH (p:Product) WHERE p.name CONTAINS 'Book' RETURN p

// Combining operations
MATCH (p:Product)
WHERE p.name STARTS WITH 'Mac' OR p.name CONTAINS 'Laptop'
RETURN p
```

---

## 17.4 Point Indexes

### Creating Point Indexes

```cypher
// Point index for spatial data
CREATE POINT INDEX location_idx FOR (p:Place) ON (p.location)

// For geographic queries
CREATE POINT INDEX store_location FOR (s:Store) ON (s.coordinates)
```

### Spatial Queries with Point Index

```cypher
// Distance query (uses index)
MATCH (s:Store)
WHERE point.distance(s.coordinates, point({latitude: 40.7, longitude: -74.0})) < 5000
RETURN s.name, point.distance(s.coordinates, point({latitude: 40.7, longitude: -74.0})) AS meters
ORDER BY meters

// Bounding box query
MATCH (p:Place)
WHERE p.location.x > -74.1 AND p.location.x < -73.9
  AND p.location.y > 40.6 AND p.location.y < 40.8
RETURN p
```

---

## 17.5 Full-Text Indexes

### Creating Full-Text Indexes

```cypher
// Full-text index on single property
CREATE FULLTEXT INDEX product_search FOR (p:Product) ON EACH [p.name, p.description]

// Full-text index on multiple labels
CREATE FULLTEXT INDEX content_search FOR (n:Article|Blog|News) ON EACH [n.title, n.body]

// With analyzer configuration
CREATE FULLTEXT INDEX product_search_configured FOR (p:Product) ON EACH [p.name]
OPTIONS {
    indexConfig: {
        `fulltext.analyzer`: 'english',
        `fulltext.eventually_consistent`: true
    }
}
```

### Querying Full-Text Indexes

```cypher
// Basic search
CALL db.index.fulltext.queryNodes('product_search', 'laptop computer')
YIELD node, score
RETURN node.name, score
ORDER BY score DESC
LIMIT 10

// Fuzzy search (typo tolerance)
CALL db.index.fulltext.queryNodes('product_search', 'labtop~')
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

// Wildcard search
CALL db.index.fulltext.queryNodes('product_search', 'lap*')
YIELD node, score
RETURN node.name, score

// Boosting terms
CALL db.index.fulltext.queryNodes('product_search', 'laptop^2 computer')
YIELD node, score
RETURN node.name, score

// Combining with Cypher filters
CALL db.index.fulltext.queryNodes('product_search', 'laptop')
YIELD node AS product, score
WHERE product.price < 1000 AND product.inStock = true
RETURN product.name, product.price, score
ORDER BY score DESC
```

### Full-Text Index Analyzers

```cypher
// List available analyzers
CALL db.index.fulltext.listAvailableAnalyzers()

// Common analyzers:
// - 'standard' - Default, good for most cases
// - 'english' - English language with stemming
// - 'simple' - Lowercase only
// - 'whitespace' - Split on whitespace only
// - 'keyword' - No tokenization
```

---

## 17.6 Managing Indexes

### Listing Indexes

```cypher
// Show all indexes
SHOW INDEXES

// Show specific index type
SHOW INDEXES WHERE type = 'RANGE'
SHOW INDEXES WHERE type = 'FULLTEXT'

// Show index details
SHOW INDEXES YIELD name, type, labelsOrTypes, properties, state
```

### Dropping Indexes

```cypher
// Drop by name
DROP INDEX person_email

// Drop if exists
DROP INDEX person_email IF EXISTS
```

### Index States

```cypher
// Check index state
SHOW INDEXES YIELD name, state

// States:
// - ONLINE: Ready to use
// - POPULATING: Being built
// - FAILED: Creation failed
```

### Waiting for Index

```cypher
// Create and wait for index to be ready
CREATE INDEX person_email FOR (p:Person) ON (p.email)

// Wait for all indexes
CALL db.awaitIndexes(300)  // Wait up to 300 seconds

// Wait for specific index
CALL db.awaitIndex('person_email', 300)
```

---

## 17.7 Index Usage Analysis

### Using EXPLAIN and PROFILE

```cypher
// EXPLAIN shows query plan without executing
EXPLAIN MATCH (p:Person {email: 'alice@example.com'}) RETURN p

// PROFILE executes and shows actual costs
PROFILE MATCH (p:Person {email: 'alice@example.com'}) RETURN p
```

### Reading Query Plans

```
// Look for these operators:
// ✅ NodeIndexSeek - Using index
// ✅ NodeUniqueIndexSeek - Using unique constraint index
// ❌ NodeByLabelScan - Scanning all nodes with label
// ❌ AllNodesScan - Scanning entire database
```

### Forcing Index Usage

```cypher
// Use index hint
MATCH (p:Person)
USING INDEX p:Person(email)
WHERE p.email = 'alice@example.com'
RETURN p

// Force scan (rare use case)
MATCH (p:Person)
USING SCAN p:Person
WHERE p.email = 'alice@example.com'
RETURN p
```

---

## 17.8 Indexing Strategies

### When to Create Indexes

Create indexes for properties that are:

1. **Frequently searched** in WHERE clauses
2. **Used for equality lookups** (`property = value`)
3. **Used for range queries** (`property > value`)
4. **Used for string pattern matching**
5. **Foreign key equivalents** (IDs used for lookups)

### Common Index Patterns

```cypher
// 1. Unique identifiers
CREATE CONSTRAINT FOR (c:Customer) REQUIRE c.id IS UNIQUE  // Creates index automatically

// 2. Lookup fields
CREATE INDEX customer_email FOR (c:Customer) ON (c.email)

// 3. Filter fields
CREATE INDEX order_status FOR (o:Order) ON (o.status)
CREATE INDEX product_category FOR (p:Product) ON (p.category)

// 4. Date ranges
CREATE INDEX order_date FOR (o:Order) ON (o.orderDate)

// 5. Text search
CREATE TEXT INDEX product_name FOR (p:Product) ON (p.name)

// 6. Spatial
CREATE POINT INDEX store_location FOR (s:Store) ON (s.location)
```

### Index Selectivity

```cypher
// High selectivity = good index candidate
// email: alice@example.com (unique or nearly unique)
// id: 12345 (unique)

// Low selectivity = may not help
// status: 'active' (if 90% of records are active)
// country: 'USA' (if most customers are from USA)

// Consider composite indexes for low selectivity
CREATE INDEX order_status_date FOR (o:Order) ON (o.status, o.orderDate)
```

---

## 17.9 Index Best Practices

### Do's

```cypher
// ✅ Index properties used in WHERE for lookups
CREATE INDEX product_sku FOR (p:Product) ON (p.sku)

// ✅ Create composite indexes for common query patterns
CREATE INDEX person_name FOR (p:Person) ON (p.lastName, p.firstName)

// ✅ Use constraints for unique properties (includes index)
CREATE CONSTRAINT FOR (u:User) REQUIRE u.email IS UNIQUE

// ✅ Index relationship properties if frequently queried
CREATE INDEX worked_at_period FOR ()-[r:WORKED_AT]-() ON (r.startDate, r.endDate)

// ✅ Use text indexes for string pattern matching
CREATE TEXT INDEX product_description FOR (p:Product) ON (p.description)
```

### Don'ts

```cypher
// ❌ Don't index everything
// Each index adds write overhead

// ❌ Don't index properties rarely used in queries
// Example: createdAt if you never query by it

// ❌ Don't create redundant indexes
CREATE INDEX person_email FOR (p:Person) ON (p.email)
CREATE INDEX person_email_name FOR (p:Person) ON (p.email, p.name)
// The second index covers email queries too

// ❌ Don't rely on index for properties with low selectivity alone
CREATE INDEX order_active FOR (o:Order) ON (o.active)  // If 99% are active
```

### Index Maintenance

```cypher
// Monitor index usage
CALL db.stats.retrieve('INDEX USAGE')

// Periodically review indexes
SHOW INDEXES YIELD name, populationPercent, type, state
WHERE state <> 'ONLINE' OR populationPercent < 100

// Drop unused indexes
// Check query patterns first, then drop
DROP INDEX unused_index IF EXISTS
```

---

## 17.10 Python Examples

```python
from neo4j import GraphDatabase

URI = "neo4j://localhost:7687"
AUTH = ("neo4j", "password")

class IndexManager:
    def __init__(self, uri, auth):
        self.driver = GraphDatabase.driver(uri, auth=auth)
    
    def close(self):
        self.driver.close()
    
    def create_indexes(self):
        """Create all required indexes for the application."""
        indexes = [
            # Range indexes
            "CREATE INDEX customer_email IF NOT EXISTS FOR (c:Customer) ON (c.email)",
            "CREATE INDEX product_sku IF NOT EXISTS FOR (p:Product) ON (p.sku)",
            "CREATE INDEX order_date IF NOT EXISTS FOR (o:Order) ON (o.orderDate)",
            
            # Text indexes
            "CREATE TEXT INDEX product_name_text IF NOT EXISTS FOR (p:Product) ON (p.name)",
            
            # Point indexes
            "CREATE POINT INDEX store_location IF NOT EXISTS FOR (s:Store) ON (s.location)",
            
            # Full-text indexes
            """CREATE FULLTEXT INDEX product_search IF NOT EXISTS 
               FOR (p:Product) ON EACH [p.name, p.description]""",
        ]
        
        with self.driver.session() as session:
            for index_query in indexes:
                try:
                    session.run(index_query)
                    print(f"Created/verified: {index_query[:50]}...")
                except Exception as e:
                    print(f"Index creation note: {e}")
    
    def wait_for_indexes(self, timeout: int = 300):
        """Wait for all indexes to be online."""
        with self.driver.session() as session:
            session.run("CALL db.awaitIndexes($timeout)", timeout=timeout)
            print(f"All indexes are online")
    
    def list_indexes(self):
        """List all indexes and their status."""
        with self.driver.session() as session:
            result = session.run("""
                SHOW INDEXES 
                YIELD name, type, labelsOrTypes, properties, state
                RETURN name, type, labelsOrTypes, properties, state
                ORDER BY type, name
            """)
            
            print("\n=== Current Indexes ===")
            for record in result:
                print(f"{record['name']:30} | {record['type']:10} | "
                      f"{record['labelsOrTypes']} | {record['properties']} | {record['state']}")
    
    def analyze_query(self, query: str, params: dict = None):
        """Analyze a query's index usage."""
        with self.driver.session() as session:
            # Use EXPLAIN to get query plan
            explain_query = f"EXPLAIN {query}"
            result = session.run(explain_query, params or {})
            plan = result.consume().plan
            
            print(f"\n=== Query Plan for ===\n{query}\n")
            self._print_plan(plan, 0)
    
    def _print_plan(self, plan, indent):
        """Recursively print query plan."""
        prefix = "  " * indent
        operator = plan.operator_type
        args = plan.arguments
        
        # Highlight index usage
        if 'Index' in operator:
            print(f"{prefix}✅ {operator}: {args.get('index', args)}")
        elif 'Scan' in operator:
            print(f"{prefix}⚠️  {operator}: {args}")
        else:
            print(f"{prefix}{operator}")
        
        for child in plan.children:
            self._print_plan(child, indent + 1)
    
    def full_text_search(self, index_name: str, query: str, limit: int = 10):
        """Perform full-text search."""
        with self.driver.session() as session:
            result = session.run("""
                CALL db.index.fulltext.queryNodes($index, $query)
                YIELD node, score
                RETURN node, score
                ORDER BY score DESC
                LIMIT $limit
            """, index=index_name, query=query, limit=limit)
            
            return [(dict(r['node']), r['score']) for r in result]

# Usage
manager = IndexManager(URI, AUTH)
try:
    # Create all indexes
    manager.create_indexes()
    manager.wait_for_indexes()
    
    # List indexes
    manager.list_indexes()
    
    # Analyze a query
    manager.analyze_query(
        "MATCH (p:Product) WHERE p.name CONTAINS 'laptop' RETURN p"
    )
    
    # Full-text search
    results = manager.full_text_search('product_search', 'gaming laptop')
    for node, score in results:
        print(f"{node.get('name')}: {score:.2f}")
        
finally:
    manager.close()
```

---

## Summary

### Index Types Quick Reference

| Type | Create Syntax | Best For |
|------|--------------|----------|
| Range | `CREATE INDEX ... ON (p.prop)` | Equality, range, prefix |
| Text | `CREATE TEXT INDEX ... ON (p.prop)` | CONTAINS, ENDS WITH |
| Point | `CREATE POINT INDEX ... ON (p.location)` | Spatial queries |
| Full-Text | `CREATE FULLTEXT INDEX ... ON EACH [...]` | Natural language search |

### Key Commands

```cypher
-- Create indexes
CREATE INDEX name FOR (n:Label) ON (n.property)
CREATE TEXT INDEX name FOR (n:Label) ON (n.property)
CREATE POINT INDEX name FOR (n:Label) ON (n.location)
CREATE FULLTEXT INDEX name FOR (n:Label) ON EACH [n.prop1, n.prop2]

-- Manage indexes
SHOW INDEXES
DROP INDEX name IF EXISTS
CALL db.awaitIndexes(300)

-- Analyze
EXPLAIN <query>
PROFILE <query>
```

---

## Exercises

### Exercise 17.1: Basic Indexes
1. Create indexes for a Customer node (email, phone, status)
2. Create a composite index for name lookup (lastName, firstName)
3. Verify indexes are online and test query performance

### Exercise 17.2: Text Search
1. Create a text index for product names
2. Write queries using CONTAINS and ENDS WITH
3. Compare performance with and without the index

### Exercise 17.3: Full-Text Search
1. Create a full-text index for article search (title, body)
2. Implement search with fuzzy matching
3. Combine full-text results with Cypher filters

### Exercise 17.4: Query Optimization
1. Use PROFILE to analyze a slow query
2. Identify missing indexes
3. Create indexes and measure improvement

---

**Next Chapter: [Chapter 18: Constraints](18-constraints.md)**
