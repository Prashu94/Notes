# Chapter 6: Cypher - Writing Data (CREATE, MERGE, SET, DELETE)

## Learning Objectives
By the end of this chapter, you will:
- Create nodes and relationships with CREATE
- Use MERGE for idempotent operations
- Update data with SET
- Remove data with DELETE and REMOVE
- Understand transactions and batch operations

---

## 6.1 The CREATE Clause

### Purpose

`CREATE` adds new nodes and relationships to the graph. It always creates new elements, even if identical ones exist.

### Creating Nodes

```cypher
// Simplest node
CREATE ()

// Node with label
CREATE (:Person)

// Node with label and properties
CREATE (:Person {name: 'Alice', age: 30})

// Node with multiple labels
CREATE (:Person:Employee:Developer {name: 'Bob'})

// Create and return the node
CREATE (p:Person {name: 'Charlie', age: 25})
RETURN p

// Create with expression
CREATE (p:Person {
    name: 'Diana',
    createdAt: datetime(),
    id: randomUUID()
})
RETURN p
```

### Creating Multiple Nodes

```cypher
// Multiple CREATE statements
CREATE (alice:Person {name: 'Alice'})
CREATE (bob:Person {name: 'Bob'})
CREATE (charlie:Person {name: 'Charlie'})
RETURN alice, bob, charlie

// Create with different labels
CREATE (person:Person {name: 'Eve'})
CREATE (company:Company {name: 'TechCorp'})
CREATE (product:Product {name: 'Widget', price: 29.99})
RETURN person, company, product
```

### Creating Relationships

```cypher
// Create relationship between new nodes
CREATE (alice:Person {name: 'Alice'})-[:KNOWS]->(bob:Person {name: 'Bob'})

// Create relationship with properties
CREATE (alice:Person {name: 'Alice'})
       -[:KNOWS {since: 2020, strength: 'close'}]->
       (bob:Person {name: 'Bob'})
RETURN alice, bob

// Create relationship between existing nodes
MATCH (alice:Person {name: 'Alice'})
MATCH (bob:Person {name: 'Bob'})
CREATE (alice)-[:KNOWS {since: 2024}]->(bob)

// Create multiple relationships
MATCH (alice:Person {name: 'Alice'})
MATCH (bob:Person {name: 'Bob'})
MATCH (charlie:Person {name: 'Charlie'})
CREATE (alice)-[:KNOWS]->(bob)
CREATE (alice)-[:KNOWS]->(charlie)
CREATE (bob)-[:KNOWS]->(charlie)
```

### Creating Complex Structures

```cypher
// Create a small network in one statement
CREATE (alice:Person {name: 'Alice'})-[:KNOWS]->(bob:Person {name: 'Bob'}),
       (alice)-[:KNOWS]->(charlie:Person {name: 'Charlie'}),
       (bob)-[:KNOWS]->(charlie),
       (bob)-[:WORKS_FOR]->(company:Company {name: 'TechCorp'}),
       (charlie)-[:WORKS_FOR]->(company)
RETURN alice, bob, charlie, company

// Create with current timestamp
CREATE (event:Event {
    name: 'Meeting',
    createdAt: datetime(),
    createdBy: 'system'
})
RETURN event
```

---

## 6.2 The MERGE Clause

### Purpose

`MERGE` ensures a pattern exists in the graph. It either matches existing data or creates new data.

**Think of it as**: "Find or Create"

### MERGE vs CREATE

| CREATE | MERGE |
|--------|-------|
| Always creates new data | Creates only if not found |
| Can create duplicates | Prevents duplicates |
| Faster (no lookup) | Slower (must check first) |
| Use when data is definitely new | Use for idempotent operations |

### Basic MERGE

```cypher
// Merge a node (create if not exists)
MERGE (p:Person {name: 'Alice'})
RETURN p

// Run again - same node returned, no duplicate
MERGE (p:Person {name: 'Alice'})
RETURN p

// Merge with multiple properties (all must match!)
MERGE (p:Person {name: 'Alice', age: 30})
RETURN p

// ⚠️ This creates a NEW node if age differs!
MERGE (p:Person {name: 'Alice', age: 31})
RETURN p
```

### MERGE with Unique Property

```cypher
// Best practice: MERGE on unique identifier only
MERGE (p:Person {email: 'alice@example.com'})
SET p.name = 'Alice', p.age = 30
RETURN p

// Or use constraint
CREATE CONSTRAINT person_email_unique 
FOR (p:Person) REQUIRE p.email IS UNIQUE

// Now MERGE is safe
MERGE (p:Person {email: 'alice@example.com'})
SET p.name = 'Alice'
RETURN p
```

### ON CREATE and ON MATCH

```cypher
// Set properties only when creating
MERGE (p:Person {email: 'alice@example.com'})
ON CREATE SET p.createdAt = datetime(),
              p.name = 'Alice'
RETURN p

// Set properties only when matching
MERGE (p:Person {email: 'alice@example.com'})
ON MATCH SET p.lastSeen = datetime()
RETURN p

// Both together
MERGE (p:Person {email: 'alice@example.com'})
ON CREATE SET p.createdAt = datetime(),
              p.name = 'Alice',
              p.visits = 1
ON MATCH SET p.lastSeen = datetime(),
             p.visits = p.visits + 1
RETURN p

// Combine with SET (runs regardless)
MERGE (p:Person {email: 'alice@example.com'})
ON CREATE SET p.createdAt = datetime()
ON MATCH SET p.visits = p.visits + 1
SET p.lastActive = datetime()  // Always runs
RETURN p
```

### MERGE Relationships

```cypher
// Merge relationship (creates if not exists)
MATCH (alice:Person {name: 'Alice'})
MATCH (bob:Person {name: 'Bob'})
MERGE (alice)-[:KNOWS]->(bob)

// Merge with properties (careful - ALL properties must match!)
MATCH (alice:Person {name: 'Alice'})
MATCH (bob:Person {name: 'Bob'})
MERGE (alice)-[r:KNOWS]->(bob)
ON CREATE SET r.since = date()
RETURN r

// Merge entire pattern (nodes and relationships)
MERGE (alice:Person {name: 'Alice'})-[:KNOWS]->(bob:Person {name: 'Bob'})
// ⚠️ If Alice exists but not Bob, creates BOTH new nodes!
```

### Safe MERGE Patterns

```cypher
// ✅ Safe: Merge nodes separately, then relationship
MERGE (alice:Person {email: 'alice@example.com'})
ON CREATE SET alice.name = 'Alice'

MERGE (bob:Person {email: 'bob@example.com'})
ON CREATE SET bob.name = 'Bob'

MERGE (alice)-[:KNOWS]->(bob)

// ✅ Safe: Match nodes, merge relationship
MATCH (alice:Person {name: 'Alice'})
MATCH (bob:Person {name: 'Bob'})
MERGE (alice)-[:KNOWS]->(bob)

// ❌ Risky: Merging entire pattern
MERGE (alice:Person {name: 'Alice'})-[:KNOWS]->(bob:Person {name: 'Bob'})
```

---

## 6.3 The SET Clause

### Purpose

`SET` updates properties on nodes and relationships, and adds labels to nodes.

### Setting Properties

```cypher
// Set a single property
MATCH (p:Person {name: 'Alice'})
SET p.age = 31
RETURN p

// Set multiple properties
MATCH (p:Person {name: 'Alice'})
SET p.age = 31,
    p.city = 'NYC',
    p.email = 'alice@example.com'
RETURN p

// Set property to expression result
MATCH (p:Person {name: 'Alice'})
SET p.updatedAt = datetime()
RETURN p

// Set property based on other property
MATCH (p:Person {name: 'Alice'})
SET p.birthYear = date().year - p.age
RETURN p
```

### Updating Multiple Nodes

```cypher
// Update all matching nodes
MATCH (p:Person)
WHERE p.city = 'New York'
SET p.city = 'NYC'
RETURN count(p) AS updated

// Conditional update
MATCH (p:Person)
SET p.status = CASE 
    WHEN p.age < 18 THEN 'minor'
    WHEN p.age < 65 THEN 'adult'
    ELSE 'senior'
END
RETURN p.name, p.status
```

### SET with Maps

```cypher
// Add/update properties from a map (+=)
MATCH (p:Person {name: 'Alice'})
SET p += {city: 'NYC', country: 'USA', verified: true}
RETURN p

// ⚠️ Replace ALL properties with map (=)
MATCH (p:Person {name: 'Alice'})
SET p = {name: 'Alice', age: 31}  // Removes all other properties!
RETURN p

// Dynamic properties from parameter
:param updates => {city: 'LA', phone: '555-1234'}

MATCH (p:Person {name: 'Alice'})
SET p += $updates
RETURN p
```

### Setting Labels

```cypher
// Add a label
MATCH (p:Person {name: 'Alice'})
SET p:Employee
RETURN p, labels(p)

// Add multiple labels
MATCH (p:Person {name: 'Alice'})
SET p:Employee:Developer
RETURN p, labels(p)

// Conditional label
MATCH (p:Person)
WHERE p.role = 'manager'
SET p:Manager
RETURN p.name
```

### Setting Relationship Properties

```cypher
// Update relationship property
MATCH (a:Person {name: 'Alice'})-[r:KNOWS]->(b:Person {name: 'Bob'})
SET r.strength = 'strong',
    r.updatedAt = datetime()
RETURN r

// Update all relationships of a type
MATCH ()-[r:KNOWS]->()
SET r.type = 'social'
RETURN count(r) AS updated
```

---

## 6.4 The REMOVE Clause

### Purpose

`REMOVE` deletes properties from nodes/relationships and removes labels from nodes.

### Removing Properties

```cypher
// Remove a single property
MATCH (p:Person {name: 'Alice'})
REMOVE p.tempData
RETURN p

// Remove multiple properties
MATCH (p:Person {name: 'Alice'})
REMOVE p.tempData, p.oldField
RETURN p

// Remove from multiple nodes
MATCH (p:Person)
WHERE p.verified = false
REMOVE p.verificationCode
RETURN count(p)
```

### Alternative: SET to NULL

```cypher
// These are equivalent:
MATCH (p:Person {name: 'Alice'})
REMOVE p.tempData

MATCH (p:Person {name: 'Alice'})
SET p.tempData = null
```

### Removing Labels

```cypher
// Remove a label
MATCH (p:Person:Temporary {name: 'Alice'})
REMOVE p:Temporary
RETURN p, labels(p)

// Remove multiple labels
MATCH (p:Person:Temp:Unverified)
REMOVE p:Temp:Unverified
RETURN p

// Conditional removal
MATCH (p:Person:Pending)
WHERE p.verified = true
REMOVE p:Pending
SET p:Verified
RETURN p
```

---

## 6.5 The DELETE Clause

### Purpose

`DELETE` removes nodes and relationships from the graph.

### Deleting Relationships

```cypher
// Delete a specific relationship
MATCH (a:Person {name: 'Alice'})-[r:KNOWS]->(b:Person {name: 'Bob'})
DELETE r
RETURN a, b

// Delete all relationships of a type between two nodes
MATCH (a:Person {name: 'Alice'})-[r]-(b:Person {name: 'Bob'})
DELETE r

// Delete all relationships of a specific type
MATCH ()-[r:TEMPORARY]->()
DELETE r

// Delete relationships matching condition
MATCH ()-[r:KNOWS]->()
WHERE r.since < date('2020-01-01')
DELETE r
```

### Deleting Nodes

```cypher
// Delete a node (must have no relationships!)
MATCH (p:Person {name: 'TempUser'})
DELETE p

// This fails if node has relationships:
// Error: Cannot delete node with relationships
```

### DETACH DELETE

```cypher
// Delete node AND all its relationships
MATCH (p:Person {name: 'Alice'})
DETACH DELETE p

// Delete multiple nodes with relationships
MATCH (p:Person)
WHERE p.status = 'deleted'
DETACH DELETE p

// Delete all data in database (⚠️ CAREFUL!)
MATCH (n)
DETACH DELETE n
```

### Conditional Deletion

```cypher
// Delete if condition met
MATCH (p:Person)
WHERE p.lastLogin < date() - duration('P365D')
DETACH DELETE p

// Delete with OPTIONAL MATCH pattern
MATCH (p:Person {name: 'Alice'})
OPTIONAL MATCH (p)-[r]-()
DELETE r, p
```

### Safe Deletion Patterns

```cypher
// Check before deleting
MATCH (p:Person {name: 'Alice'})
OPTIONAL MATCH (p)-[r]-()
RETURN p, count(r) AS relationshipCount

// Delete in controlled batches
CALL {
    MATCH (p:Person)
    WHERE p.status = 'deleted'
    WITH p LIMIT 1000
    DETACH DELETE p
    RETURN count(*) AS deleted
} IN TRANSACTIONS OF 1000 ROWS
RETURN deleted
```

---

## 6.6 FOREACH Clause

### Purpose

`FOREACH` allows operations on each element in a list, typically for batch updates within a single query.

### Basic FOREACH

```cypher
// Update multiple nodes from a list
WITH ['Alice', 'Bob', 'Charlie'] AS names
FOREACH (name IN names |
    MERGE (p:Person {name: name})
)

// Set property on all nodes in a path
MATCH path = (a:Person {name: 'Alice'})-[:KNOWS*]->(b:Person)
FOREACH (node IN nodes(path) |
    SET node.visited = true
)
```

### FOREACH with Index

```cypher
// Create nodes with index
WITH ['Apple', 'Banana', 'Cherry'] AS fruits
FOREACH (i IN range(0, size(fruits)-1) |
    CREATE (:Fruit {name: fruits[i], order: i})
)
```

### Practical FOREACH Examples

```cypher
// Create relationships from a list
MATCH (alice:Person {name: 'Alice'})
WITH alice, ['Bob', 'Charlie', 'Diana'] AS friendNames
FOREACH (name IN friendNames |
    MERGE (friend:Person {name: name})
    CREATE (alice)-[:KNOWS]->(friend)
)

// Mark all nodes in a path
MATCH path = shortestPath((start:Person {name: 'Alice'})-[*]-(end:Person {name: 'Eve'}))
FOREACH (n IN nodes(path) | SET n.inShortestPath = true)
FOREACH (r IN relationships(path) | SET r.inShortestPath = true)
```

---

## 6.7 Batch Operations

### Using UNWIND for Batch Creates

```cypher
// Create multiple nodes from a list
UNWIND [{name: 'Alice', age: 30}, {name: 'Bob', age: 28}] AS personData
CREATE (p:Person)
SET p = personData
RETURN p

// Create with parameter
:param people => [{name: 'Alice', age: 30}, {name: 'Bob', age: 28}]

UNWIND $people AS personData
MERGE (p:Person {name: personData.name})
SET p.age = personData.age
RETURN p
```

### Batch Updates with CALL IN TRANSACTIONS

```cypher
// Process large datasets in batches
CALL {
    MATCH (p:Person)
    WHERE p.status = 'pending'
    SET p.processed = true
    RETURN count(*) AS processed
} IN TRANSACTIONS OF 1000 ROWS

// Batch delete
CALL {
    MATCH (n:TempNode)
    WITH n LIMIT 10000
    DETACH DELETE n
    RETURN count(*) AS deleted
} IN TRANSACTIONS OF 5000 ROWS
```

### Using Python for Batch Operations

```python
from neo4j import GraphDatabase

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))

def batch_create_people(tx, people):
    tx.run("""
        UNWIND $people AS person
        MERGE (p:Person {email: person.email})
        ON CREATE SET p.name = person.name,
                      p.createdAt = datetime()
        ON MATCH SET p.name = person.name,
                     p.updatedAt = datetime()
    """, people=people)

# Process in batches
people = [{"name": f"Person{i}", "email": f"person{i}@example.com"} 
          for i in range(10000)]

batch_size = 1000
with driver.session() as session:
    for i in range(0, len(people), batch_size):
        batch = people[i:i + batch_size]
        session.execute_write(batch_create_people, batch)
        print(f"Processed {min(i + batch_size, len(people))} records")

driver.close()
```

---

## 6.8 Transaction Management

### Implicit Transactions

```cypher
// Each query in Neo4j Browser is a transaction
CREATE (p:Person {name: 'Alice'})
RETURN p
// Auto-commits on success, auto-rollbacks on failure
```

### Explicit Transactions in Python

```python
from neo4j import GraphDatabase

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))

# Using session.execute_write for write transactions
def create_person(tx, name, age):
    result = tx.run("""
        CREATE (p:Person {name: $name, age: $age, created: datetime()})
        RETURN p
    """, name=name, age=age)
    return result.single()

with driver.session() as session:
    # This runs in a transaction
    person = session.execute_write(create_person, "Alice", 30)
    print(f"Created: {person}")

# Using session.execute_read for read transactions
def find_person(tx, name):
    result = tx.run("""
        MATCH (p:Person {name: $name})
        RETURN p
    """, name=name)
    return result.single()

with driver.session() as session:
    person = session.execute_read(find_person, "Alice")
    print(f"Found: {person}")

driver.close()
```

### Transaction with Multiple Operations

```python
def transfer_funds(tx, from_account, to_account, amount):
    # Verify source account has sufficient funds
    result = tx.run("""
        MATCH (from:Account {id: $from_id})
        RETURN from.balance AS balance
    """, from_id=from_account)
    
    balance = result.single()["balance"]
    if balance < amount:
        raise ValueError("Insufficient funds")
    
    # Perform the transfer
    tx.run("""
        MATCH (from:Account {id: $from_id})
        MATCH (to:Account {id: $to_id})
        SET from.balance = from.balance - $amount,
            to.balance = to.balance + $amount
        CREATE (from)-[:TRANSFERRED {
            amount: $amount, 
            timestamp: datetime()
        }]->(to)
    """, from_id=from_account, to_id=to_account, amount=amount)

# The transaction is atomic
with driver.session() as session:
    try:
        session.execute_write(transfer_funds, "ACC001", "ACC002", 100)
        print("Transfer successful")
    except Exception as e:
        print(f"Transfer failed: {e}")
        # Transaction is automatically rolled back
```

---

## 6.9 Best Practices for Writing Data

### 1. Use Constraints for Data Integrity

```cypher
// Create unique constraint
CREATE CONSTRAINT person_email_unique 
FOR (p:Person) REQUIRE p.email IS UNIQUE

// Create existence constraint (Enterprise)
CREATE CONSTRAINT person_name_exists 
FOR (p:Person) REQUIRE p.name IS NOT NULL
```

### 2. Use MERGE Instead of CREATE for Deduplication

```cypher
// ❌ May create duplicates
CREATE (p:Person {email: 'alice@example.com'})

// ✅ Idempotent - safe to run multiple times
MERGE (p:Person {email: 'alice@example.com'})
ON CREATE SET p.name = 'Alice'
```

### 3. Separate Node and Relationship MERGE

```cypher
// ❌ Risky pattern
MERGE (a:Person {name: 'Alice'})-[:KNOWS]->(b:Person {name: 'Bob'})

// ✅ Safe pattern
MERGE (a:Person {name: 'Alice'})
MERGE (b:Person {name: 'Bob'})
MERGE (a)-[:KNOWS]->(b)
```

### 4. Use Parameters

```cypher
// ❌ Hardcoded values
CREATE (p:Person {name: 'Alice', age: 30})

// ✅ Parameterized
CREATE (p:Person {name: $name, age: $age})
```

### 5. Batch Large Operations

```cypher
// ❌ Single large transaction
UNWIND range(1, 1000000) AS i
CREATE (:Node {id: i})

// ✅ Batched transactions
CALL {
    UNWIND range(1, 1000000) AS i
    CREATE (:Node {id: i})
} IN TRANSACTIONS OF 10000 ROWS
```

---

## Summary

### Key Takeaways

| Clause | Purpose | Creates Duplicates? |
|--------|---------|---------------------|
| **CREATE** | Always creates new data | Yes |
| **MERGE** | Find or create | No |
| **SET** | Update properties/labels | N/A |
| **REMOVE** | Delete properties/labels | N/A |
| **DELETE** | Delete nodes/relationships | N/A |
| **DETACH DELETE** | Delete nodes with relationships | N/A |

### Quick Reference

```cypher
-- Create
CREATE (n:Label {prop: value})
CREATE (a)-[:TYPE]->(b)

-- Merge (find or create)
MERGE (n:Label {key: value})
ON CREATE SET n.created = datetime()
ON MATCH SET n.updated = datetime()

-- Update
SET n.prop = value
SET n += {map}
SET n:NewLabel

-- Remove property/label
REMOVE n.prop
REMOVE n:Label

-- Delete
DELETE r                    -- Delete relationship
DELETE n                    -- Delete node (no relationships)
DETACH DELETE n             -- Delete node and all relationships
```

---

## Exercises

### Exercise 6.1: Create Operations
1. Create a movie database with 5 movies, 5 actors, and 3 directors
2. Create relationships for who acted in and directed which movies
3. Add genre nodes and connect movies to them

### Exercise 6.2: MERGE Practice
1. Create a script that can be run multiple times without creating duplicates
2. Use ON CREATE and ON MATCH to track creation and access times
3. Merge a complex pattern of users and their purchases

### Exercise 6.3: Update Operations
1. Update all movies released before 2000 to add a "classic" label
2. Increase all product prices by 10%
3. Add a "verified" property to all users who have email

### Exercise 6.4: Delete Operations
1. Remove all "temporary" labels from nodes
2. Delete all relationships older than a certain date
3. Create a safe delete function that archives before deleting

### Exercise 6.5: Batch Operations
1. Create a batch import for 1000 products from a list
2. Update all user statuses in batches
3. Implement a bulk delete with progress tracking

---

**Next Chapter: [Chapter 7: Cypher - Filtering and Sorting](07-cypher-filtering-sorting.md)**
