# Chapter 3: Graph Database Concepts

## Learning Objectives
By the end of this chapter, you will:
- Understand nodes, relationships, properties, and labels in depth
- Know the property graph model used by Neo4j
- Understand traversals and paths
- Learn naming conventions and best practices
- Be able to design basic graph structures

---

## 3.1 The Property Graph Model

Neo4j uses the **Property Graph Model**, which consists of four building blocks:

```
┌─────────────────────────────────────────────────────────────┐
│              PROPERTY GRAPH MODEL COMPONENTS                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. NODES (Vertices)                                        │
│     • Represent entities/objects                            │
│     • Can have labels                                       │
│     • Can have properties                                   │
│                                                             │
│  2. RELATIONSHIPS (Edges)                                   │
│     • Connect nodes                                         │
│     • Have exactly one type                                 │
│     • Have a direction                                      │
│     • Can have properties                                   │
│                                                             │
│  3. LABELS                                                  │
│     • Categorize nodes                                      │
│     • Nodes can have multiple labels                        │
│     • Enable efficient querying                             │
│                                                             │
│  4. PROPERTIES                                              │
│     • Key-value pairs                                       │
│     • Stored on nodes and relationships                     │
│     • Various data types supported                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Visual Representation

```
                    LABEL: Person
                         │
                         ▼
    ┌─────────────────────────────────────┐
    │  ┌─────────────────────────────────┐│
    │  │         NODE                    ││
    │  │                                 ││
    │  │  name: "Alice"    ◄─ Property   ││
    │  │  age: 30          ◄─ Property   ││
    │  │  email: "a@x.com" ◄─ Property   ││
    │  │                                 ││
    │  └─────────────────────────────────┘│
    └─────────────────────────────────────┘
              │
              │  RELATIONSHIP
              │  Type: KNOWS
              │  Direction: outgoing
              │  Properties: {since: 2020}
              ▼
    ┌─────────────────────────────────────┐
    │  ┌─────────────────────────────────┐│
    │  │         NODE                    ││
    │  │                                 ││
    │  │  name: "Bob"                    ││
    │  │  age: 28                        ││
    │  │                                 ││
    │  └─────────────────────────────────┘│
    └─────────────────────────────────────┘
               LABEL: Person
```

---

## 3.2 Nodes in Detail

### What are Nodes?

Nodes represent **entities** or **objects** in your domain:
- People, places, things
- Events, concepts, categories
- Any discrete object you want to model

### Creating Nodes

```cypher
// Simplest node (no label, no properties)
CREATE ()

// Node with one label
CREATE (:Person)

// Node with properties
CREATE ({name: 'Alice', age: 30})

// Node with label and properties (most common)
CREATE (:Person {name: 'Alice', age: 30})

// Node with multiple labels
CREATE (:Person:Employee:Developer {name: 'Alice'})

// Create and return the node
CREATE (p:Person {name: 'Alice', age: 30})
RETURN p
```

### Node Identity

Every node has a unique internal ID assigned by Neo4j:

```cypher
// Get node's element ID (recommended)
MATCH (p:Person {name: 'Alice'})
RETURN elementId(p) AS nodeId

// Old method (deprecated)
MATCH (p:Person {name: 'Alice'})
RETURN id(p) AS legacyId
```

⚠️ **Note**: Internal IDs can be reused after deletion. Use your own unique identifiers for application logic.

### Node Example: Multiple Entities

```cypher
// Create different types of nodes
CREATE (:Person {name: 'Alice', born: 1985})
CREATE (:Company {name: 'TechCorp', founded: 2010})
CREATE (:Product {name: 'Widget', price: 29.99})
CREATE (:City {name: 'New York', country: 'USA'})
CREATE (:Event {name: 'Conference 2024', date: date('2024-06-15')})
```

---

## 3.3 Labels in Detail

### What are Labels?

Labels are **tags** that categorize nodes:
- Enable efficient querying (like table names in SQL)
- Allow multiple categorizations
- Can be added/removed dynamically

### Label Characteristics

| Feature | Description |
|---------|-------------|
| Case-sensitive | `:Person` ≠ `:person` ≠ `:PERSON` |
| Multiple allowed | A node can have 0 to many labels |
| Dynamic | Labels can be added/removed at runtime |
| Indexable | Labels are used for index lookups |

### Working with Labels

```cypher
// Create node with multiple labels
CREATE (a:Person:Actor:Producer {name: 'Tom Hanks'})

// Add a label to existing node
MATCH (p:Person {name: 'Alice'})
SET p:Employee

// Remove a label
MATCH (p:Person {name: 'Alice'})
REMOVE p:Employee

// Check if node has label
MATCH (p:Person)
WHERE p:Employee
RETURN p.name

// Get all labels of a node
MATCH (p:Person {name: 'Alice'})
RETURN labels(p) AS nodeLabels
```

### Using Labels for State

Labels can represent states or temporary conditions:

```cypher
// Mark an order as shipped
MATCH (o:Order {id: '12345'})
SET o:Shipped

// Mark a user as verified
MATCH (u:User {email: 'alice@example.com'})
SET u:Verified

// Find all pending orders
MATCH (o:Order)
WHERE NOT o:Shipped AND NOT o:Cancelled
RETURN o
```

### Label Naming Conventions

```
✅ DO:
   - Use PascalCase: Person, MovieGenre, UserAccount
   - Use singular nouns: Person (not Persons)
   - Be specific: Vehicle, Car, Motorcycle

❌ DON'T:
   - Use snake_case: user_account
   - Use plurals: Persons, Movies
   - Use verbs: Running, Completed (use for states only)
```

---

## 3.4 Relationships in Detail

### What are Relationships?

Relationships **connect** nodes and represent:
- How entities relate to each other
- Actions between entities
- Associations, memberships, hierarchies

### Relationship Characteristics

| Feature | Description |
|---------|-------------|
| **Direction** | Always have a direction (outgoing/incoming) |
| **Type** | Must have exactly one type |
| **Properties** | Can have key-value properties |
| **Connectivity** | Connect exactly two nodes |
| **Self-relationships** | A node can relate to itself |

### Creating Relationships

```cypher
// Basic relationship (create nodes and relationship)
CREATE (alice:Person {name: 'Alice'})
CREATE (bob:Person {name: 'Bob'})
CREATE (alice)-[:KNOWS]->(bob)

// Relationship with properties
CREATE (alice)-[:KNOWS {since: 2020, strength: 'close'}]->(bob)

// Create relationship between existing nodes
MATCH (alice:Person {name: 'Alice'})
MATCH (bob:Person {name: 'Bob'})
CREATE (alice)-[:FRIENDS_WITH {since: 2020}]->(bob)

// Self-relationship (node relating to itself)
MATCH (p:Person {name: 'Alice'})
CREATE (p)-[:MANAGES]->(p)
```

### Relationship Direction

```
Direction Matters for Semantics:
─────────────────────────────────

(Alice)-[:KNOWS]->(Bob)
Alice knows Bob (Alice → Bob)

(Alice)<-[:KNOWS]-(Bob)
Bob knows Alice (Bob → Alice)

(Alice)-[:KNOWS]-(Bob)
Either direction (pattern matching)
```

**When Querying**: You can ignore direction if it doesn't matter:

```cypher
// Find any KNOWS relationship regardless of direction
MATCH (alice:Person {name: 'Alice'})-[:KNOWS]-(friend)
RETURN friend.name

// Find outgoing KNOWS relationships
MATCH (alice:Person {name: 'Alice'})-[:KNOWS]->(friend)
RETURN friend.name

// Find incoming KNOWS relationships
MATCH (alice:Person {name: 'Alice'})<-[:KNOWS]-(friend)
RETURN friend.name
```

### Relationship Types

```cypher
// Different relationship types
CREATE (alice:Person {name: 'Alice'})
CREATE (company:Company {name: 'TechCorp'})
CREATE (product:Product {name: 'Widget'})
CREATE (city:City {name: 'New York'})

CREATE (alice)-[:WORKS_FOR {since: 2020, position: 'Engineer'}]->(company)
CREATE (alice)-[:LIVES_IN {since: 2018}]->(city)
CREATE (alice)-[:PURCHASED {date: date('2024-01-15'), amount: 29.99}]->(product)
CREATE (company)-[:LOCATED_IN]->(city)
CREATE (company)-[:SELLS]->(product)
```

### Relationship Type Naming Conventions

```
✅ DO:
   - Use SCREAMING_SNAKE_CASE: WORKS_FOR, ACTED_IN
   - Use verbs: KNOWS, LIKES, PURCHASED
   - Be specific: AUTHORED (not HAS_RELATIONSHIP)

❌ DON'T:
   - Use camelCase: worksFor
   - Use spaces: WORKS FOR
   - Be generic: RELATED_TO, HAS
```

### Multiple Relationships Between Same Nodes

```cypher
// A person can have multiple relationships with another person
MATCH (alice:Person {name: 'Alice'})
MATCH (bob:Person {name: 'Bob'})

CREATE (alice)-[:KNOWS {since: 2015}]->(bob)
CREATE (alice)-[:WORKS_WITH {project: 'ProjectX'}]->(bob)
CREATE (alice)-[:MANAGES]->(bob)
```

### Query Specific Relationship Types

```cypher
// Find one type
MATCH (p:Person)-[:WORKS_FOR]->(c:Company)
RETURN p.name, c.name

// Find multiple types (OR)
MATCH (p:Person)-[:KNOWS|FRIENDS_WITH]->(other:Person)
RETURN p.name, other.name

// Find any relationship
MATCH (p:Person)-[r]->(other)
RETURN p.name, type(r), other
```

---

## 3.5 Properties in Detail

### What are Properties?

Properties are **key-value pairs** that store data on nodes and relationships:
- Descriptive attributes
- Identifiers
- Metrics and measurements
- Timestamps

### Supported Property Types

| Type | Examples | Notes |
|------|----------|-------|
| **Boolean** | `true`, `false` | |
| **Integer** | `42`, `-17`, `0` | 64-bit signed |
| **Float** | `3.14`, `-2.5` | 64-bit double |
| **String** | `'Hello'`, `"World"` | UTF-8 encoded |
| **Date** | `date('2024-01-15')` | ISO 8601 |
| **Time** | `time('12:30:00')` | With timezone |
| **DateTime** | `datetime('2024-01-15T12:30:00')` | Full timestamp |
| **Duration** | `duration('P1Y2M3D')` | ISO 8601 |
| **Point** | `point({x:1, y:2})` | Spatial |
| **List** | `[1, 2, 3]`, `['a', 'b']` | Homogeneous |

### Working with Properties

```cypher
// Create node with various property types
CREATE (p:Product {
  name: 'Widget',                           // String
  price: 29.99,                             // Float
  quantity: 100,                            // Integer
  inStock: true,                            // Boolean
  tags: ['electronics', 'gadgets'],         // List of strings
  createdAt: datetime(),                    // Current datetime
  releaseDate: date('2024-01-15'),          // Date
  location: point({latitude: 40.7, longitude: -74.0})  // Point
})
RETURN p
```

### Setting and Updating Properties

```cypher
// Set a single property
MATCH (p:Person {name: 'Alice'})
SET p.email = 'alice@example.com'

// Set multiple properties
MATCH (p:Person {name: 'Alice'})
SET p.email = 'alice@example.com',
    p.phone = '555-1234',
    p.verified = true

// Set properties from a map
MATCH (p:Person {name: 'Alice'})
SET p += {city: 'NYC', country: 'USA'}

// Replace all properties (careful!)
MATCH (p:Person {name: 'Alice'})
SET p = {name: 'Alice', age: 31}  // Removes all other properties!
```

### Removing Properties

```cypher
// Remove a property
MATCH (p:Person {name: 'Alice'})
REMOVE p.email

// Set property to null (same as removing)
MATCH (p:Person {name: 'Alice'})
SET p.email = null
```

### Property Naming Conventions

```
✅ DO:
   - Use camelCase: firstName, createdAt, isActive
   - Use descriptive names: purchaseDate, totalAmount
   - Be consistent: createdAt/updatedAt (not created_at/updatedAt)

❌ DON'T:
   - Use spaces: first name
   - Use special characters: $price, user-id
   - Use reserved words: type, id (use different names)
```

---

## 3.6 Traversals and Paths

### What is a Traversal?

A **traversal** is the process of navigating the graph by following relationships from node to node.

```
Traversal Example:
Start at Alice → Follow KNOWS → Reach Bob → Follow WORKS_FOR → Reach Company

(Alice)-[:KNOWS]->(Bob)-[:WORKS_FOR]->(TechCorp)
```

### What is a Path?

A **path** is a sequence of alternating nodes and relationships:

```
Path Structure:
Node → Relationship → Node → Relationship → Node → ...

Path Length = Number of Relationships
```

### Path Examples

```cypher
// Return a path
MATCH path = (alice:Person {name: 'Alice'})-[:KNOWS]->(bob:Person)-[:WORKS_FOR]->(company:Company)
RETURN path

// Path with variable length
MATCH path = (start:Person {name: 'Alice'})-[:KNOWS*1..3]->(end:Person)
RETURN path, length(path) AS pathLength

// Get nodes and relationships from path
MATCH path = (a)-[*]->(b)
WHERE a.name = 'Alice' AND b.name = 'Company'
RETURN nodes(path) AS allNodes, relationships(path) AS allRels
```

### Path Length

```
Path Length 0: Just a node
(Alice)

Path Length 1: One relationship
(Alice)-[:KNOWS]->(Bob)

Path Length 2: Two relationships
(Alice)-[:KNOWS]->(Bob)-[:WORKS_FOR]->(Company)

Path Length N: N relationships
(A)-[r1]->(B)-[r2]->(C)-...-[rN]->(Z)
```

### Variable-Length Paths

```cypher
// Exactly 2 hops
MATCH (a)-[:KNOWS*2]->(b)
RETURN a.name, b.name

// 1 to 3 hops
MATCH (a)-[:KNOWS*1..3]->(b)
RETURN a.name, b.name

// 0 or more hops (includes self)
MATCH (a)-[:KNOWS*0..]->(b)
RETURN a.name, b.name

// Any number of hops (careful - can be expensive!)
MATCH (a)-[:KNOWS*]->(b)
RETURN a.name, b.name
```

### Shortest Path

```cypher
// Find shortest path between two nodes
MATCH (alice:Person {name: 'Alice'}), (charlie:Person {name: 'Charlie'})
MATCH path = shortestPath((alice)-[*]-(charlie))
RETURN path, length(path)

// All shortest paths
MATCH (alice:Person {name: 'Alice'}), (charlie:Person {name: 'Charlie'})
MATCH path = allShortestPaths((alice)-[*]-(charlie))
RETURN path, length(path)

// Shortest path with specific relationship types
MATCH (alice:Person {name: 'Alice'}), (charlie:Person {name: 'Charlie'})
MATCH path = shortestPath((alice)-[:KNOWS|WORKS_WITH*]-(charlie))
RETURN path
```

---

## 3.7 Graph Patterns

### Pattern Matching Syntax

```cypher
// Basic patterns
()                          // Any node
(n)                         // Node bound to variable n
(:Person)                   // Node with label Person
(p:Person)                  // Node with label, bound to p
(p:Person {name: 'Alice'})  // Node with label and property

// Relationship patterns
()-[]-()                    // Any relationship, any direction
()-[]->()                   // Any relationship, outgoing
()<-[]-()                   // Any relationship, incoming
()-[:KNOWS]-()              // KNOWS relationship
()-[r:KNOWS]-()             // KNOWS relationship, bound to r
()-[r:KNOWS {since: 2020}]->()  // With property
()-[:KNOWS|FRIENDS_WITH]-() // Multiple types (OR)
```

### Complex Patterns

```cypher
// Chain of relationships
MATCH (a)-[:KNOWS]->(b)-[:WORKS_FOR]->(c)
RETURN a, b, c

// Multiple relationships from same node
MATCH (p:Person)-[:KNOWS]->(friend),
      (p)-[:WORKS_FOR]->(company)
RETURN p.name, friend.name, company.name

// Triangle pattern
MATCH (a)-[:KNOWS]->(b)-[:KNOWS]->(c)-[:KNOWS]->(a)
RETURN a.name, b.name, c.name
```

### Pattern Example: Social Network

```cypher
// Create a small social network
CREATE (alice:Person {name: 'Alice'})
CREATE (bob:Person {name: 'Bob'})
CREATE (charlie:Person {name: 'Charlie'})
CREATE (diana:Person {name: 'Diana'})

CREATE (alice)-[:KNOWS {since: 2015}]->(bob)
CREATE (alice)-[:KNOWS {since: 2018}]->(charlie)
CREATE (bob)-[:KNOWS {since: 2016}]->(charlie)
CREATE (charlie)-[:KNOWS {since: 2019}]->(diana)
CREATE (bob)-[:KNOWS {since: 2020}]->(diana)

// Find friends of friends
MATCH (alice:Person {name: 'Alice'})-[:KNOWS]->(friend)-[:KNOWS]->(fof)
WHERE fof <> alice
RETURN DISTINCT fof.name AS friendOfFriend

// Find mutual friends
MATCH (alice:Person {name: 'Alice'})-[:KNOWS]->(mutual)<-[:KNOWS]-(bob:Person {name: 'Bob'})
RETURN mutual.name AS mutualFriend
```

---

## 3.8 Schema Concepts

### Schema-Optional Nature

Neo4j is **schema-optional**:
- You can create data without defining schema first
- Schema (indexes, constraints) can be added later
- Flexible for evolving data models

### Index Types Overview

| Index Type | Use Case |
|------------|----------|
| **Range** | General-purpose lookups |
| **Text** | String prefix/suffix searches |
| **Point** | Spatial queries |
| **Full-text** | Natural language search |
| **Vector** | Similarity search |
| **Token Lookup** | Internal use |

### Constraint Types Overview

| Constraint Type | Purpose |
|-----------------|---------|
| **Uniqueness** | Ensure property values are unique |
| **Existence** | Ensure property exists (Enterprise) |
| **Type** | Ensure property has correct type (Enterprise) |
| **Key** | Combination of uniqueness + existence (Enterprise) |

### Creating Basic Schema

```cypher
// Create uniqueness constraint (also creates index)
CREATE CONSTRAINT person_name_unique IF NOT EXISTS
FOR (p:Person) REQUIRE p.name IS UNIQUE

// Create index for faster lookups
CREATE INDEX person_age_index IF NOT EXISTS
FOR (p:Person) ON (p.age)

// Show all constraints
SHOW CONSTRAINTS

// Show all indexes
SHOW INDEXES
```

---

## 3.9 Naming Conventions Summary

### Complete Naming Guide

```
┌─────────────────────────────────────────────────────────────┐
│              NEO4J NAMING CONVENTIONS                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ELEMENT          CONVENTION          EXAMPLES              │
│  ───────          ──────────          ────────              │
│  Labels           PascalCase          Person                │
│                                       MovieGenre            │
│                                       UserAccount           │
│                                                             │
│  Relationship     SCREAMING_SNAKE     ACTED_IN              │
│  Types            _CASE               WORKS_FOR             │
│                                       FRIENDS_WITH          │
│                                                             │
│  Properties       camelCase           firstName             │
│                                       createdAt             │
│                                       isActive              │
│                                                             │
│  Variables        camelCase           person                │
│  (in queries)                         movieTitle            │
│                                       totalCount            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Examples in Practice

```cypher
// Good naming example
CREATE (john:Person:Employee {
    firstName: 'John',
    lastName: 'Smith',
    dateOfBirth: date('1985-03-15'),
    isManager: true
})

CREATE (acme:Company {
    companyName: 'ACME Corp',
    foundedYear: 2010,
    isPublic: false
})

CREATE (john)-[:WORKS_FOR {
    startDate: date('2020-01-15'),
    department: 'Engineering',
    isFullTime: true
}]->(acme)
```

---

## 3.10 Complete Example: Building a Graph

### Domain: Movie Database

Let's build a complete movie database graph:

```cypher
// Clear existing data (careful in production!)
MATCH (n) DETACH DELETE n

// Create Movie nodes
CREATE (inception:Movie {
    title: 'Inception',
    released: 2010,
    tagline: 'Your mind is the scene of the crime',
    budget: 160000000,
    revenue: 836836967
})

CREATE (darkKnight:Movie {
    title: 'The Dark Knight',
    released: 2008,
    tagline: 'Why So Serious?',
    budget: 185000000,
    revenue: 1004558444
})

CREATE (interstellar:Movie {
    title: 'Interstellar',
    released: 2014,
    tagline: 'Mankind was born on Earth. It was never meant to die here.',
    budget: 165000000,
    revenue: 677471339
})

// Create Person nodes
CREATE (nolan:Person {
    name: 'Christopher Nolan',
    born: 1970,
    nationality: 'British'
})

CREATE (leo:Person {
    name: 'Leonardo DiCaprio',
    born: 1974,
    nationality: 'American'
})

CREATE (christian:Person {
    name: 'Christian Bale',
    born: 1974,
    nationality: 'British'
})

CREATE (matthew:Person {
    name: 'Matthew McConaughey',
    born: 1969,
    nationality: 'American'
})

CREATE (anne:Person {
    name: 'Anne Hathaway',
    born: 1982,
    nationality: 'American'
})

// Create Genre nodes
CREATE (scifi:Genre {name: 'Sci-Fi'})
CREATE (action:Genre {name: 'Action'})
CREATE (thriller:Genre {name: 'Thriller'})
CREATE (drama:Genre {name: 'Drama'})

// Create DIRECTED relationships
CREATE (nolan)-[:DIRECTED]->(inception)
CREATE (nolan)-[:DIRECTED]->(darkKnight)
CREATE (nolan)-[:DIRECTED]->(interstellar)

// Create ACTED_IN relationships with roles
CREATE (leo)-[:ACTED_IN {roles: ['Dom Cobb'], billing: 1}]->(inception)
CREATE (christian)-[:ACTED_IN {roles: ['Bruce Wayne', 'Batman'], billing: 1}]->(darkKnight)
CREATE (matthew)-[:ACTED_IN {roles: ['Cooper'], billing: 1}]->(interstellar)
CREATE (anne)-[:ACTED_IN {roles: ['Amelia Brand'], billing: 2}]->(interstellar)
CREATE (anne)-[:ACTED_IN {roles: ['Catwoman'], billing: 2}]->(darkKnight)

// Create IN_GENRE relationships
CREATE (inception)-[:IN_GENRE]->(scifi)
CREATE (inception)-[:IN_GENRE]->(action)
CREATE (inception)-[:IN_GENRE]->(thriller)
CREATE (darkKnight)-[:IN_GENRE]->(action)
CREATE (darkKnight)-[:IN_GENRE]->(thriller)
CREATE (darkKnight)-[:IN_GENRE]->(drama)
CREATE (interstellar)-[:IN_GENRE]->(scifi)
CREATE (interstellar)-[:IN_GENRE]->(drama)
```

### Query the Movie Graph

```cypher
// Find all movies directed by Nolan
MATCH (nolan:Person {name: 'Christopher Nolan'})-[:DIRECTED]->(movie:Movie)
RETURN movie.title, movie.released
ORDER BY movie.released

// Find actors in Interstellar
MATCH (actor:Person)-[r:ACTED_IN]->(movie:Movie {title: 'Interstellar'})
RETURN actor.name, r.roles

// Find actors who worked with Nolan multiple times
MATCH (actor:Person)-[:ACTED_IN]->(movie:Movie)<-[:DIRECTED]-(nolan:Person {name: 'Christopher Nolan'})
WITH actor, count(movie) AS movieCount
WHERE movieCount > 1
RETURN actor.name, movieCount

// Find all Sci-Fi movies
MATCH (movie:Movie)-[:IN_GENRE]->(genre:Genre {name: 'Sci-Fi'})
RETURN movie.title

// Find movies with both Action and Thriller genres
MATCH (movie:Movie)-[:IN_GENRE]->(g1:Genre {name: 'Action'})
MATCH (movie)-[:IN_GENRE]->(g2:Genre {name: 'Thriller'})
RETURN movie.title

// Find actors who acted together
MATCH (actor1:Person)-[:ACTED_IN]->(movie:Movie)<-[:ACTED_IN]-(actor2:Person)
WHERE actor1.name < actor2.name  // Avoid duplicates
RETURN actor1.name, actor2.name, movie.title
```

---

## Summary

### Key Takeaways

1. **Property Graph Model**: Nodes, relationships, labels, and properties
2. **Nodes**: Represent entities, can have multiple labels
3. **Relationships**: Connect nodes, have type and direction
4. **Properties**: Key-value pairs on nodes and relationships
5. **Paths**: Sequences of nodes and relationships
6. **Naming**: PascalCase labels, SCREAMING_SNAKE_CASE types, camelCase properties

### Graph Building Checklist

✅ Identify entities → Nodes  
✅ Categorize entities → Labels  
✅ Identify connections → Relationships  
✅ Name connections → Relationship types  
✅ Add descriptive data → Properties  
✅ Follow naming conventions  

---

## Exercises

### Exercise 3.1: Model Your Domain
Choose a domain (e.g., library system, restaurant reviews) and:
1. Identify at least 3 node types
2. Define their labels
3. List relevant properties for each
4. Identify relationships between them

### Exercise 3.2: Create a Graph
Using the domain from 3.1, write Cypher to:
1. Create 5-10 nodes of different types
2. Create relationships between them
3. Add meaningful properties

### Exercise 3.3: Query Patterns
Write queries to answer these questions about your graph:
1. Find all nodes of a specific type
2. Find nodes connected by a specific relationship
3. Find paths between two nodes
4. Count nodes by label

### Exercise 3.4: Extend the Movie Graph
Add to the movie graph example:
1. 3 more movies
2. 3 more actors
3. User nodes who RATED movies (with rating property)
4. Query to find highest-rated movies

---

**Next Chapter: [Chapter 4: Cypher Fundamentals](04-cypher-fundamentals.md)**
