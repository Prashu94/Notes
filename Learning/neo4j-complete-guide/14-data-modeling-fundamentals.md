# Chapter 14: Data Modeling Fundamentals

## Learning Objectives
By the end of this chapter, you will:
- Understand graph data modeling principles
- Design effective node and relationship structures
- Choose between properties and relationships
- Apply naming conventions and best practices
- Convert relational models to graph models

---

## 14.1 Graph Modeling Philosophy

### Think in Connections

Unlike relational databases that focus on tables and joins, graph databases prioritize:

1. **Entities as Nodes**: Things that exist independently
2. **Connections as Relationships**: How things relate to each other
3. **Attributes as Properties**: Characteristics of nodes and relationships
4. **Categories as Labels**: Types or roles of nodes

### The Whiteboard Model

One of Neo4j's strengths is that your conceptual model maps directly to the implementation:

```
Whiteboard:
  [Alice] --knows--> [Bob] --works_at--> [Acme Corp]

Cypher:
  (alice:Person {name: 'Alice'})-[:KNOWS]->(bob:Person {name: 'Bob'})-[:WORKS_AT]->(acme:Company {name: 'Acme Corp'})
```

### Questions to Ask

1. **What are the main entities?** → Nodes
2. **How do entities relate?** → Relationships
3. **What describes each entity?** → Properties
4. **What categories exist?** → Labels

---

## 14.2 Node Design

### When to Create a Node

Create a node when something:
- Has an independent identity
- Has multiple properties
- Can be connected to multiple other things
- Might be queried directly

### Example: E-commerce Domain

```cypher
// Good node candidates
(:Customer {id: 'C001', name: 'Alice', email: 'alice@example.com'})
(:Product {sku: 'SKU123', name: 'Laptop', price: 999.99})
(:Order {id: 'O001', orderDate: date('2026-01-25'), total: 1099.99})
(:Category {name: 'Electronics'})
(:Address {street: '123 Main St', city: 'NYC', zip: '10001'})
```

### Node Identity

Every node should have a way to be uniquely identified:

```cypher
// Option 1: Natural key (domain-specific)
CREATE CONSTRAINT FOR (p:Product) REQUIRE p.sku IS UNIQUE

// Option 2: Business key (UUID)
CREATE CONSTRAINT FOR (c:Customer) REQUIRE c.customerId IS UNIQUE

// Option 3: Composite key
CREATE CONSTRAINT FOR (e:Employee) REQUIRE (e.company, e.employeeNumber) IS UNIQUE
```

### When NOT to Create a Node

Don't create a node for:
- Simple enumerated values (use properties or labels)
- Attributes that don't need relationships
- Values only used with one other entity

```cypher
// ❌ Over-modeling: Status as a node
(:Order)-[:HAS_STATUS]->(:Status {name: 'Pending'})

// ✅ Better: Status as a property
(:Order {status: 'Pending'})

// ✅ Or as a label for frequent queries
(:Order:Pending {id: 'O001'})
```

---

## 14.3 Relationship Design

### Relationship Fundamentals

Relationships have:
- **Direction**: Always stored with direction (but can be queried both ways)
- **Type**: The relationship name (verb phrase)
- **Properties**: Optional attributes on the relationship

### Naming Conventions

```cypher
// Use UPPER_SNAKE_CASE for relationship types
// Use verb phrases that read naturally

// Good relationship names
(:Person)-[:KNOWS]->(:Person)
(:Customer)-[:PLACED]->(:Order)
(:Order)-[:CONTAINS]->(:Product)
(:Employee)-[:WORKS_FOR]->(:Company)
(:Employee)-[:REPORTS_TO]->(:Employee)
(:Product)-[:BELONGS_TO]->(:Category)

// Avoid vague names
// ❌ Bad
(:Person)-[:RELATED_TO]->(:Person)
(:Order)-[:HAS]->(:Product)

// ✅ Better
(:Person)-[:MARRIED_TO]->(:Person)
(:Order)-[:CONTAINS]->(:Product)
```

### Relationship Direction

Choose direction based on the domain, not query patterns:

```cypher
// Direction follows natural language
(:Customer)-[:PLACED]->(:Order)     // Customer places order
(:Employee)-[:REPORTS_TO]->(:Manager)  // Employee reports to manager
(:Person)-[:FOLLOWS]->(:Person)     // Alice follows Bob

// Symmetric relationships: pick one direction, query both ways
(:Person)-[:FRIENDS_WITH]->(:Person)

// Query ignoring direction
MATCH (p1:Person)-[:FRIENDS_WITH]-(p2:Person)
WHERE p1.name = 'Alice'
RETURN p2.name
```

### When to Use Relationship Properties

```cypher
// Properties describe the relationship, not the connected nodes
(:Person)-[:KNOWS {since: 2020, context: 'work'}]->(:Person)
(:Customer)-[:PURCHASED {quantity: 2, price: 49.99}]->(:Product)
(:Employee)-[:WORKED_FOR {from: date('2020-01-01'), to: date('2023-12-31')}]->(:Company)

// Time-dependent data
(:Person)-[:RATED {rating: 5, timestamp: datetime()}]->(:Movie)
```

---

## 14.4 Properties vs Relationships

### When to Use Properties

Use properties when the value:
- Is a simple data type (string, number, date, etc.)
- Doesn't need its own relationships
- Won't be queried for connections

```cypher
// Good as properties
(:Person {
    name: 'Alice',
    email: 'alice@example.com',
    birthDate: date('1990-05-15'),
    active: true
})

// Good: Status as property (simple enumeration)
(:Order {status: 'Pending'})
```

### When to Use Relationships

Use relationships when:
- The connection carries meaning
- You need to traverse through it
- Multiple entities share the same value
- The related thing has its own properties or relationships

```cypher
// Address: Might be shared, has its own properties
(:Person)-[:LIVES_AT]->(:Address {street: '123 Main', city: 'NYC'})
(:Company)-[:LOCATED_AT]->(:Address)

// Category: Hierarchical, used for navigation
(:Product)-[:IN_CATEGORY]->(:Category)-[:SUBCATEGORY_OF]->(:Category)

// Tag: Many-to-many, queryable
(:Article)-[:TAGGED_WITH]->(:Tag {name: 'Neo4j'})
(:Video)-[:TAGGED_WITH]->(:Tag {name: 'Neo4j'})
```

### The "Intermediate Node" Pattern

When a relationship needs to connect to other things, create an intermediate node:

```cypher
// ❌ Can't connect a relationship to another node
(:Person)-[:EMPLOYED_BY {role: 'Engineer', department: ???}]->(:Company)

// ✅ Use intermediate node
(:Person)-[:HAS_POSITION]->(:Position {role: 'Engineer', startDate: date('2020-01-01')})-[:AT_COMPANY]->(:Company)
(:Position)-[:IN_DEPARTMENT]->(:Department)
```

---

## 14.5 Labels Best Practices

### Label Purpose

Labels serve multiple purposes:
1. **Type identification**: What kind of thing is this?
2. **Index targeting**: Which nodes to index
3. **Query filtering**: Narrow down starting points

### Single vs Multiple Labels

```cypher
// Single primary label
(:Person)
(:Company)
(:Product)

// Multiple labels for roles/states
(:Person:Employee:Manager)  // Person who is an Employee and a Manager
(:Person:Customer)          // Person who is a Customer
(:Order:Pending)            // Order that is Pending
(:Order:Shipped)            // Order that is Shipped

// Use multiple labels for:
// - Temporary states
// - Roles that overlap
// - Performance optimization (querying specific subsets)
```

### Label Naming Conventions

```cypher
// Use PascalCase (UpperCamelCase)
// Use singular nouns

// ✅ Good
:Person
:Company
:ProductCategory
:ShippingAddress

// ❌ Bad
:persons        // Plural
:product_category  // Snake case
:COMPANY        // All caps
```

### When to Add/Remove Labels Dynamically

```cypher
// Track state changes with labels
MATCH (o:Order {id: $orderId})
REMOVE o:Pending
SET o:Shipped

// Query specific states efficiently
MATCH (o:Order:Pending)
WHERE o.orderDate < date() - duration('P7D')
RETURN o AS overdueOrders

// Use labels for temporary classifications
MATCH (c:Customer)
WHERE NOT EXISTS { (c)-[:PLACED]->(:Order) WHERE o.date > date() - duration('P1Y') }
SET c:Inactive
```

---

## 14.6 Converting from Relational Models

### Tables to Nodes

```sql
-- Relational: Customers table
CREATE TABLE customers (
    id INT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100),
    created_at TIMESTAMP
);
```

```cypher
// Graph: Customer nodes
CREATE (c:Customer {
    id: 1,
    name: 'Alice',
    email: 'alice@example.com',
    createdAt: datetime('2026-01-01T00:00:00Z')
})

CREATE CONSTRAINT FOR (c:Customer) REQUIRE c.id IS UNIQUE
```

### Foreign Keys to Relationships

```sql
-- Relational: Orders with foreign key
CREATE TABLE orders (
    id INT PRIMARY KEY,
    customer_id INT REFERENCES customers(id),
    order_date DATE,
    total DECIMAL(10,2)
);
```

```cypher
// Graph: Order node with relationship to Customer
MATCH (c:Customer {id: 1})
CREATE (o:Order {id: 101, orderDate: date('2026-01-25'), total: 199.99})
CREATE (c)-[:PLACED]->(o)
```

### Join Tables to Relationships

```sql
-- Relational: Many-to-many with join table
CREATE TABLE order_items (
    order_id INT REFERENCES orders(id),
    product_id INT REFERENCES products(id),
    quantity INT,
    unit_price DECIMAL(10,2),
    PRIMARY KEY (order_id, product_id)
);
```

```cypher
// Graph: Relationship with properties
MATCH (o:Order {id: 101}), (p:Product {id: 'SKU123'})
CREATE (o)-[:CONTAINS {quantity: 2, unitPrice: 49.99}]->(p)
```

### Self-Referencing Tables

```sql
-- Relational: Employee hierarchy
CREATE TABLE employees (
    id INT PRIMARY KEY,
    name VARCHAR(100),
    manager_id INT REFERENCES employees(id)
);
```

```cypher
// Graph: Natural self-relationship
MATCH (e:Employee {id: 1}), (m:Employee {id: 2})
CREATE (e)-[:REPORTS_TO]->(m)

// Query hierarchy naturally
MATCH path = (e:Employee)-[:REPORTS_TO*]->(ceo:Employee)
WHERE NOT (ceo)-[:REPORTS_TO]->()
RETURN e.name, length(path) AS level
```

---

## 14.7 Common Graph Patterns

### Hierarchical Data

```cypher
// Organization hierarchy
(:Company)-[:HAS_DEPARTMENT]->(:Department)-[:HAS_TEAM]->(:Team)
(:Employee)-[:MEMBER_OF]->(:Team)
(:Employee)-[:REPORTS_TO]->(:Employee)

// Category hierarchy
(:Category {name: 'Electronics'})
  -[:HAS_SUBCATEGORY]->(:Category {name: 'Computers'})
    -[:HAS_SUBCATEGORY]->(:Category {name: 'Laptops'})

// Query all ancestors
MATCH (p:Product {name: 'MacBook'})-[:IN_CATEGORY]->(cat:Category)
MATCH path = (cat)-[:SUBCATEGORY_OF*0..]->(ancestor:Category)
RETURN collect(DISTINCT ancestor.name) AS categoryPath
```

### Time-Based Data

```cypher
// Event tracking
(:User)-[:PERFORMED {timestamp: datetime()}]->(:Action {type: 'login'})

// State history
(:Order)-[:HAD_STATUS]->(:OrderStatus {
    status: 'Pending',
    from: datetime('2026-01-25T10:00:00Z'),
    to: datetime('2026-01-25T14:00:00Z')
})

// Version history
(:Document {id: 'D001'})-[:HAS_VERSION]->(:DocumentVersion {
    version: 1,
    content: '...',
    createdAt: datetime(),
    createdBy: 'user1'
})
```

### Social Network

```cypher
// Connections
(:Person)-[:FOLLOWS]->(:Person)
(:Person)-[:FRIENDS_WITH]->(:Person)
(:Person)-[:BLOCKED]->(:Person)

// Content
(:Person)-[:POSTED]->(:Post)-[:HAS_COMMENT]->(:Comment)
(:Person)-[:LIKES]->(:Post)
(:Post)-[:TAGGED_WITH]->(:Topic)

// Friend of friend query
MATCH (me:Person {id: $userId})-[:FRIENDS_WITH]->(friend)-[:FRIENDS_WITH]->(fof:Person)
WHERE NOT (me)-[:FRIENDS_WITH]->(fof) AND me <> fof
RETURN fof, count(friend) AS mutualFriends
ORDER BY mutualFriends DESC
```

### Knowledge Graph

```cypher
// Entities and relationships
(:Person {name: 'Albert Einstein'})-[:BORN_IN]->(:City {name: 'Ulm'})
(:Person {name: 'Albert Einstein'})-[:DEVELOPED]->(:Theory {name: 'General Relativity'})
(:Theory {name: 'General Relativity'})-[:RELATES_TO]->(:Concept {name: 'Spacetime'})
(:Person {name: 'Albert Einstein'})-[:WORKED_AT]->(:Institution {name: 'Princeton'})

// Flexible schema allows new relationship types
(:Person)-[:INFLUENCED]->(:Person)
(:Theory)-[:SUPERSEDES]->(:Theory)
(:Concept)-[:PART_OF]->(:Field)
```

---

## 14.8 Design Decisions Checklist

### Before Creating a Node

- [ ] Does it have an independent identity?
- [ ] Will it have multiple relationships?
- [ ] Will you query for it directly?
- [ ] Does it have meaningful properties beyond just a name?

### Before Creating a Relationship

- [ ] Does the connection have semantic meaning?
- [ ] Is the relationship type descriptive (verb phrase)?
- [ ] Is the direction meaningful in your domain?
- [ ] Do you need properties on this connection?

### Before Adding a Property

- [ ] Is it a simple value type?
- [ ] Does it only apply to this entity?
- [ ] Will you filter/sort by this property? (consider indexing)
- [ ] Could it be a relationship instead?

### Before Adding a Label

- [ ] Does it represent a meaningful category?
- [ ] Will you query specifically for this category?
- [ ] Is it stable enough (not changing constantly)?
- [ ] Could you use a property instead?

---

## 14.9 Modeling Exercise: E-commerce

### Requirements

- Customers can place orders
- Orders contain products with quantities
- Products belong to categories (hierarchical)
- Customers have shipping addresses
- Products have reviews from customers

### Initial Model

```cypher
// Nodes
(:Customer {id, name, email, createdAt})
(:Order {id, orderDate, status, total})
(:Product {sku, name, description, price, stock})
(:Category {id, name, description})
(:Address {id, street, city, state, zip, country})
(:Review {id, rating, title, content, createdAt})

// Relationships
(:Customer)-[:PLACED]->(:Order)
(:Customer)-[:HAS_ADDRESS {type: 'shipping'|'billing', isDefault: boolean}]->(:Address)
(:Order)-[:SHIPPED_TO]->(:Address)
(:Order)-[:CONTAINS {quantity, unitPrice}]->(:Product)
(:Product)-[:IN_CATEGORY]->(:Category)
(:Category)-[:SUBCATEGORY_OF]->(:Category)
(:Customer)-[:WROTE]->(:Review)-[:REVIEWS]->(:Product)
```

### Cypher Implementation

```cypher
// Create constraints
CREATE CONSTRAINT customer_id FOR (c:Customer) REQUIRE c.id IS UNIQUE;
CREATE CONSTRAINT product_sku FOR (p:Product) REQUIRE p.sku IS UNIQUE;
CREATE CONSTRAINT order_id FOR (o:Order) REQUIRE o.id IS UNIQUE;
CREATE CONSTRAINT category_id FOR (cat:Category) REQUIRE cat.id IS UNIQUE;

// Create sample data
CREATE (c:Customer {id: 'C001', name: 'Alice', email: 'alice@example.com'})
CREATE (addr:Address {id: 'A001', street: '123 Main St', city: 'NYC', zip: '10001'})
CREATE (c)-[:HAS_ADDRESS {type: 'shipping', isDefault: true}]->(addr)

CREATE (electronics:Category {id: 'CAT001', name: 'Electronics'})
CREATE (computers:Category {id: 'CAT002', name: 'Computers'})
CREATE (laptops:Category {id: 'CAT003', name: 'Laptops'})
CREATE (computers)-[:SUBCATEGORY_OF]->(electronics)
CREATE (laptops)-[:SUBCATEGORY_OF]->(computers)

CREATE (p:Product {sku: 'SKU001', name: 'MacBook Pro', price: 1999.99})
CREATE (p)-[:IN_CATEGORY]->(laptops)

CREATE (o:Order {id: 'O001', orderDate: date('2026-01-25'), status: 'Pending', total: 1999.99})
CREATE (c)-[:PLACED]->(o)
CREATE (o)-[:SHIPPED_TO]->(addr)
CREATE (o)-[:CONTAINS {quantity: 1, unitPrice: 1999.99}]->(p)

CREATE (r:Review {id: 'R001', rating: 5, title: 'Great laptop!', createdAt: datetime()})
CREATE (c)-[:WROTE]->(r)
CREATE (r)-[:REVIEWS]->(p)
```

---

## Summary

### Key Principles

1. **Model the domain naturally** - Graph should reflect how you think about the data
2. **Nodes for entities** - Things with identity and multiple connections
3. **Relationships for connections** - Meaningful links between entities
4. **Properties for attributes** - Simple values that describe nodes/relationships
5. **Labels for categories** - Types and roles for efficient querying

### Quick Reference

| Element | When to Use | Naming |
|---------|-------------|--------|
| Node | Independent entity | `PascalCase` label |
| Relationship | Meaningful connection | `UPPER_SNAKE_CASE` |
| Property | Simple attribute | `camelCase` |
| Label | Category/type | `PascalCase` |

---

## Exercises

### Exercise 14.1: Model a Library System
Design a graph model for:
- Books with authors (multiple authors possible)
- Library members who borrow books
- Book copies and their availability
- Book categories/genres

### Exercise 14.2: Convert a Relational Schema
Convert this relational schema to a graph model:
- Students (id, name, enrollment_date)
- Courses (id, name, credits)
- Enrollments (student_id, course_id, grade, semester)
- Professors (id, name, department)
- Course_Instructors (course_id, professor_id, semester)

### Exercise 14.3: Social Media Platform
Design a graph model for:
- Users with profiles
- Posts, comments, and likes
- Follow relationships
- Hashtags and mentions
- Private messages

### Exercise 14.4: Refactoring Exercise
Identify improvements in this model:
```cypher
(:User {name, city, country})-[:BOUGHT {product_name, price, quantity}]->(:Order)
```

---

**Next Chapter: [Chapter 15: Data Modeling Patterns](15-data-modeling-patterns.md)**
