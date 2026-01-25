# Chapter 16: Data Modeling Anti-Patterns

## Learning Objectives
By the end of this chapter, you will:
- Identify common graph modeling mistakes
- Understand performance implications of bad patterns
- Refactor problematic models
- Avoid relational thinking in graph design

---

## 16.1 The "Rich Relationship" Anti-Pattern

### Problem: Too Many Properties on Relationships

```cypher
// ❌ Anti-pattern: Relationship with many properties
(:Person)-[:EMPLOYED_BY {
    title: 'Senior Engineer',
    department: 'Engineering',
    manager: 'John Smith',
    startDate: date('2020-01-15'),
    salary: 120000,
    benefits: ['health', 'dental', '401k'],
    office: 'Building A, Floor 3',
    parkingSpot: 'A-123',
    equipment: ['laptop', 'monitor', 'keyboard']
}]->(:Company)
```

### Problems

- Can't query by department efficiently
- Can't find all employees of a manager
- Benefits can't have their own properties
- No way to share office or equipment data

### Solution: Intermediate Node

```cypher
// ✅ Better: Employment as a node
(:Person)-[:HAS_EMPLOYMENT]->(:Employment {
    title: 'Senior Engineer',
    startDate: date('2020-01-15'),
    salary: 120000
})-[:AT_COMPANY]->(:Company)

(:Employment)-[:IN_DEPARTMENT]->(:Department {name: 'Engineering'})
(:Employment)-[:REPORTS_TO]->(:Person {name: 'John Smith'})
(:Employment)-[:HAS_BENEFIT]->(:BenefitPlan {type: 'health'})
(:Employment)-[:ASSIGNED_OFFICE]->(:Office {building: 'A', floor: 3})
(:Employment)-[:ASSIGNED_EQUIPMENT]->(:Equipment {type: 'laptop'})
```

---

## 16.2 The "Dense Node" Anti-Pattern (Supernodes)

### Problem: Nodes with Millions of Relationships

```cypher
// ❌ Anti-pattern: Celebrity with millions of followers
(:Person {name: 'Celebrity'})<-[:FOLLOWS]-(:Person)  // 10 million relationships

// This query becomes very slow
MATCH (c:Person {name: 'Celebrity'})<-[:FOLLOWS]-(follower)
RETURN count(follower)
```

### Problems

- Traversing through supernode is expensive
- Lock contention during writes
- Memory pressure during queries

### Solutions

**1. Fan-Out Pattern (Bucketing)**

```cypher
// ✅ Create intermediate bucket nodes
(:Person {name: 'Celebrity'})-[:HAS_FOLLOWER_BUCKET]->(:FollowerBucket {bucketId: 1})
(:FollowerBucket {bucketId: 1})<-[:IN_BUCKET]-(:Person)  // Max 10,000 per bucket

// Query through buckets
MATCH (c:Person {name: 'Celebrity'})-[:HAS_FOLLOWER_BUCKET]->(b:FollowerBucket)
MATCH (b)<-[:IN_BUCKET]-(follower)
RETURN count(follower)
```

**2. Materialized Counts**

```cypher
// ✅ Store counts as properties
(:Person {name: 'Celebrity', followerCount: 10000000})

// Update count periodically or with triggers
MATCH (c:Person {name: 'Celebrity'})
SET c.followerCount = c.followerCount + 1
```

**3. Separate by Time/Category**

```cypher
// ✅ Partition relationships
(:Person)-[:FOLLOWED_IN_2024]->(:Person {name: 'Celebrity'})
(:Person)-[:FOLLOWED_IN_2025]->(:Person {name: 'Celebrity'})
(:Person)-[:FOLLOWED_IN_2026]->(:Person {name: 'Celebrity'})
```

---

## 16.3 The "Indexed Property Lookup" Anti-Pattern

### Problem: Using Properties Instead of Relationships

```cypher
// ❌ Anti-pattern: Storing IDs instead of relationships
(:Order {
    customerId: 'C001',
    productIds: ['P001', 'P002', 'P003'],
    shippingAddressId: 'A001'
})

// Requires multiple lookups
MATCH (o:Order {id: 'O001'})
MATCH (c:Customer {id: o.customerId})
MATCH (p:Product) WHERE p.id IN o.productIds
RETURN o, c, collect(p)
```

### Why It's Bad

- Loses the power of graph traversal
- Requires index lookups instead of pointer following
- Can't use relationship properties
- More complex queries

### Solution: Use Relationships

```cypher
// ✅ Use relationships for connections
(:Customer)-[:PLACED]->(:Order)-[:CONTAINS]->(:Product)
(:Order)-[:SHIPPED_TO]->(:Address)

// Simple traversal
MATCH (c:Customer)-[:PLACED]->(o:Order)-[:CONTAINS]->(p:Product)
WHERE o.id = 'O001'
RETURN c, o, collect(p)
```

---

## 16.4 The "Labels as Data" Anti-Pattern

### Problem: Encoding Data Values as Labels

```cypher
// ❌ Anti-pattern: Dynamic labels for values
(:Product:Electronics:InStock:OnSale:Featured)
(:Product:Clothing:OutOfStock)
(:Product:Books:InStock:OnClearance)

// Querying requires knowing all possible labels
MATCH (p:Product:InStock:OnSale)
RETURN p
```

### Problems

- Can't parameterize label queries easily
- Labels are meant for types, not states
- Difficult to query "all products with status X"
- Schema becomes unclear

### Solution: Use Properties or Relationships

```cypher
// ✅ Option 1: Properties for states
(:Product {
    category: 'Electronics',
    inStock: true,
    onSale: true,
    featured: true
})

MATCH (p:Product)
WHERE p.inStock = true AND p.onSale = true
RETURN p

// ✅ Option 2: Relationship to status/category nodes
(:Product)-[:IN_CATEGORY]->(:Category {name: 'Electronics'})
(:Product)-[:HAS_STATUS]->(:Status {name: 'InStock'})
(:Product)-[:HAS_PROMOTION]->(:Promotion {type: 'OnSale'})
```

### Exception: Labels for Major Types

Labels are appropriate for stable, mutually exclusive types:

```cypher
// ✅ Good use of labels
(:Person:Employee)  // Type of person
(:Person:Customer)  // Type of person
(:Account:Savings)  // Type of account
(:Account:Checking) // Type of account
```

---

## 16.5 The "Missing Relationship Type" Anti-Pattern

### Problem: Generic Relationship Types

```cypher
// ❌ Anti-pattern: All relationships are "RELATED_TO"
(:Person)-[:RELATED_TO {type: 'knows'}]->(:Person)
(:Person)-[:RELATED_TO {type: 'married_to'}]->(:Person)
(:Person)-[:RELATED_TO {type: 'works_with'}]->(:Person)
(:Person)-[:RELATED_TO {type: 'parent_of'}]->(:Person)

// Query requires filtering
MATCH (p:Person)-[r:RELATED_TO]->(other)
WHERE r.type = 'married_to'
RETURN other
```

### Problems

- Loses semantic meaning
- Can't optimize queries by relationship type
- Index on relationship type is not usable
- Queries are slower and less readable

### Solution: Specific Relationship Types

```cypher
// ✅ Use meaningful relationship types
(:Person)-[:KNOWS]->(:Person)
(:Person)-[:MARRIED_TO]->(:Person)
(:Person)-[:WORKS_WITH]->(:Person)
(:Person)-[:PARENT_OF]->(:Person)

// Efficient query
MATCH (p:Person)-[:MARRIED_TO]->(spouse)
RETURN spouse
```

---

## 16.6 The "Disconnected Subgraph" Anti-Pattern

### Problem: Islands of Unconnected Data

```cypher
// ❌ Anti-pattern: No connections between related data
(:Customer {id: 'C001', name: 'Alice'})
(:Order {id: 'O001', customerId: 'C001'})  // Just a property reference
(:Product {id: 'P001', orderId: 'O001'})   // Another property reference

// These form disconnected islands in the graph
```

### Why It's Bad

- Can't traverse between related entities
- Requires multiple index lookups
- Not using the graph for what it's best at
- Might as well use a relational database

### Solution: Connect Everything

```cypher
// ✅ Everything is connected
(:Customer)-[:PLACED]->(:Order)-[:CONTAINS]->(:Product)
(:Customer)-[:LIVES_AT]->(:Address)
(:Order)-[:SHIPPED_TO]->(:Address)
(:Product)-[:IN_CATEGORY]->(:Category)

// Now traversal works naturally
MATCH path = (c:Customer)-[*1..3]-(related)
WHERE c.id = 'C001'
RETURN path
```

---

## 16.7 The "Attribute as Node" Anti-Pattern

### Problem: Over-Normalizing Simple Attributes

```cypher
// ❌ Anti-pattern: Simple values as nodes
(:Person)-[:HAS_AGE]->(:Age {value: 30})
(:Person)-[:HAS_NAME]->(:Name {value: 'Alice'})
(:Person)-[:HAS_EMAIL]->(:Email {value: 'alice@example.com'})
```

### Why It's Bad

- Unnecessary complexity
- More nodes and relationships to manage
- Slower queries
- No benefit over properties

### When to Use Nodes vs Properties

```cypher
// ✅ Properties for simple values
(:Person {name: 'Alice', age: 30, email: 'alice@example.com'})

// ✅ Nodes when:
// - Value is shared (e.g., Address used by multiple people)
// - Value has its own properties (e.g., Email with verified flag)
// - Value participates in relationships (e.g., City with population)

(:Person)-[:LIVES_AT]->(:Address {street: '123 Main', city: 'NYC'})
(:Person)-[:HAS_EMAIL]->(:Email {address: 'alice@example.com', verified: true, verifiedAt: datetime()})
(:Person)-[:LIVES_IN]->(:City {name: 'NYC', population: 8000000})-[:IN_STATE]->(:State {name: 'NY'})
```

---

## 16.8 The "Timestamp Property" Anti-Pattern

### Problem: Losing History with Overwritten Timestamps

```cypher
// ❌ Anti-pattern: Single timestamp that gets overwritten
(:Order {
    id: 'O001',
    status: 'Shipped',
    updatedAt: datetime()  // Previous values lost
})
```

### Problems

- No history of status changes
- Can't answer "when did it change to X?"
- Can't audit changes

### Solution: Event/History Pattern

```cypher
// ✅ Track state changes
(:Order {id: 'O001', status: 'Shipped'})
    -[:HAD_STATUS]->(:StatusChange {
        status: 'Pending',
        timestamp: datetime('2026-01-20T10:00:00Z'),
        changedBy: 'system'
    })
    -[:HAD_STATUS]->(:StatusChange {
        status: 'Processing',
        timestamp: datetime('2026-01-21T14:00:00Z'),
        changedBy: 'warehouse'
    })
    -[:HAD_STATUS]->(:StatusChange {
        status: 'Shipped',
        timestamp: datetime('2026-01-22T09:00:00Z'),
        changedBy: 'shipping'
    })

// Query history
MATCH (o:Order {id: 'O001'})-[:HAD_STATUS]->(s:StatusChange)
RETURN s.status, s.timestamp, s.changedBy
ORDER BY s.timestamp
```

---

## 16.9 The "Wrong Relationship Direction" Anti-Pattern

### Problem: Inconsistent or Confusing Directions

```cypher
// ❌ Anti-pattern: Directions don't make semantic sense
(:Customer)<-[:PLACED]-(:Order)      // Order placed customer? 
(:Department)-[:WORKS_IN]->(:Employee)  // Department works in employee?

// ❌ Anti-pattern: Inconsistent directions for same relationship type
(:Person)-[:KNOWS]->(:Person)
(:Person)<-[:KNOWS]-(:Person)  // Same relationship, opposite direction
```

### Solution: Follow Natural Language

```cypher
// ✅ Directions follow natural language
(:Customer)-[:PLACED]->(:Order)        // Customer placed order
(:Employee)-[:WORKS_IN]->(:Department) // Employee works in department

// ✅ Symmetric relationships: pick one direction, query both ways
(:Person)-[:FRIENDS_WITH]->(:Person)  // Consistent direction

// Query ignoring direction when appropriate
MATCH (p1:Person)-[:FRIENDS_WITH]-(p2:Person)
WHERE p1.name = 'Alice'
RETURN p2.name
```

---

## 16.10 Refactoring Examples

### Example 1: From Relational to Graph

```cypher
// ❌ Before: Relational thinking
(:Order {
    orderId: 'O001',
    customerId: 'C001',
    customerName: 'Alice',        // Denormalized
    productIds: ['P001', 'P002'],
    productNames: ['Widget', 'Gadget'],  // Denormalized
    total: 149.99
})

// ✅ After: Graph thinking
(:Customer {id: 'C001', name: 'Alice'})
    -[:PLACED]->(:Order {id: 'O001', total: 149.99})
    -[:CONTAINS {quantity: 1, unitPrice: 49.99}]->(:Product {id: 'P001', name: 'Widget'})

(:Order {id: 'O001'})
    -[:CONTAINS {quantity: 2, unitPrice: 50.00}]->(:Product {id: 'P002', name: 'Gadget'})
```

### Example 2: From Dense Properties to Relationships

```cypher
// ❌ Before: Properties encode relationships
(:Movie {
    title: 'Inception',
    directorName: 'Christopher Nolan',
    actorNames: ['Leonardo DiCaprio', 'Ellen Page', 'Tom Hardy'],
    genres: ['Sci-Fi', 'Thriller'],
    productionCompany: 'Warner Bros'
})

// ✅ After: Proper relationships
(:Movie {title: 'Inception'})
    -[:DIRECTED_BY]->(:Person {name: 'Christopher Nolan'})
    
(:Person {name: 'Leonardo DiCaprio'})-[:ACTED_IN {role: 'Cobb'}]->(:Movie {title: 'Inception'})
(:Person {name: 'Ellen Page'})-[:ACTED_IN {role: 'Ariadne'}]->(:Movie {title: 'Inception'})

(:Movie {title: 'Inception'})
    -[:IN_GENRE]->(:Genre {name: 'Sci-Fi'})
    -[:IN_GENRE]->(:Genre {name: 'Thriller'})
    -[:PRODUCED_BY]->(:Company {name: 'Warner Bros'})
```

### Example 3: Breaking Up Supernodes

```cypher
// ❌ Before: Global category node
(:Category {name: 'All Products'})<-[:IN_CATEGORY]-(:Product)  // Millions of products

// ✅ After: Hierarchical categories
(:Category {name: 'All Products'})
    -[:HAS_SUBCATEGORY]->(:Category {name: 'Electronics'})
        -[:HAS_SUBCATEGORY]->(:Category {name: 'Computers'})
            -[:HAS_SUBCATEGORY]->(:Category {name: 'Laptops'})
            
(:Product)-[:IN_CATEGORY]->(:Category {name: 'Laptops'})  // Leaf categories only

// Query with traversal
MATCH (root:Category {name: 'Electronics'})-[:HAS_SUBCATEGORY*0..]->(cat:Category)
MATCH (p:Product)-[:IN_CATEGORY]->(cat)
RETURN count(p) AS productsInElectronics
```

---

## Summary

### Anti-Pattern Quick Reference

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| Rich Relationship | Too many properties on relationship | Intermediate node |
| Dense Node (Supernode) | Millions of relationships | Bucketing, materialized counts |
| Indexed Property Lookup | IDs instead of relationships | Use relationships |
| Labels as Data | Dynamic labels for values | Properties or relationship to status nodes |
| Missing Relationship Type | Generic RELATED_TO | Specific relationship types |
| Disconnected Subgraph | No connections | Connect everything |
| Attribute as Node | Over-normalization | Use properties for simple values |
| Timestamp Property | Lost history | Event/history pattern |
| Wrong Direction | Confusing semantics | Follow natural language |

### Key Questions for Model Review

1. Are relationships being used for connections?
2. Do relationship types have semantic meaning?
3. Are there supernodes that need refactoring?
4. Is history being preserved where needed?
5. Can you traverse naturally through the model?

---

## Exercises

### Exercise 16.1: Identify Anti-Patterns
Review this model and identify all anti-patterns:
```cypher
(:User {
    userId: 'U001',
    friendIds: ['U002', 'U003', 'U004'],
    status: 'active'
})-[:RELATED_TO {type: 'follows'}]->(:User)

(:Post:Featured:Trending {
    postId: 'P001',
    authorId: 'U001',
    likes: 1500000,
    updatedAt: datetime()
})-[:HAS_TAG]->(:Tag {value: 'neo4j'})
```

### Exercise 16.2: Refactor a Model
Refactor this e-commerce model:
```cypher
(:Order {
    orderId: 'O001',
    customerId: 'C001',
    customerEmail: 'alice@test.com',
    items: [{productId: 'P001', qty: 2}, {productId: 'P002', qty: 1}],
    status: 'shipped',
    statusChangedAt: datetime()
})
```

### Exercise 16.3: Supernode Resolution
Design a solution for a social network where:
- Some users have millions of followers
- Need to query "who follows user X?"
- Need to count followers efficiently
- Need to check "does A follow B?"

---

**Next Chapter: [Chapter 17: Indexes](17-indexes.md)**
