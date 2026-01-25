# Chapter 15: Data Modeling Patterns

## Learning Objectives
By the end of this chapter, you will:
- Apply common graph modeling patterns
- Handle time-based and versioned data
- Model complex relationships effectively
- Implement authorization and access control patterns
- Design for specific use cases

---

## 15.1 The Intermediate Node Pattern

### When Relationships Need More Connections

When a relationship needs to connect to other nodes, promote it to an intermediate node:

```cypher
// Problem: Employment has multiple aspects
// ❌ Can't connect relationship to department
(:Person)-[:WORKS_FOR {department: 'Engineering'}]->(:Company)

// ✅ Solution: Intermediate Employment node
(:Person)-[:HAS_EMPLOYMENT]->(:Employment {
    title: 'Senior Engineer',
    startDate: date('2020-01-15'),
    salary: 120000
})-[:AT_COMPANY]->(:Company)

(:Employment)-[:IN_DEPARTMENT]->(:Department)
(:Employment)-[:HAS_BENEFIT]->(:BenefitPlan)
```

### Real-World Examples

```cypher
// Academic: Student enrollment in courses
(:Student)-[:HAS_ENROLLMENT]->(:Enrollment {
    semester: 'Fall 2026',
    grade: 'A',
    enrolledAt: datetime()
})-[:FOR_COURSE]->(:Course)
(:Enrollment)-[:WITH_INSTRUCTOR]->(:Professor)

// E-commerce: Order line items
(:Order)-[:HAS_LINE_ITEM]->(:LineItem {
    quantity: 2,
    unitPrice: 49.99,
    discount: 0.10
})-[:FOR_PRODUCT]->(:Product)

// Medical: Patient visits
(:Patient)-[:HAD_VISIT]->(:Visit {
    date: date('2026-01-25'),
    type: 'Checkup',
    notes: '...'
})-[:AT_FACILITY]->(:Hospital)
(:Visit)-[:WITH_DOCTOR]->(:Doctor)
(:Visit)-[:RESULTED_IN]->(:Diagnosis)
```

---

## 15.2 Time-Based Patterns

### Event Sourcing

Track every change as an event:

```cypher
// Event nodes
(:Account {id: 'A001'})-[:HAS_EVENT]->(:AccountEvent {
    type: 'DEPOSIT',
    amount: 1000,
    timestamp: datetime(),
    balance: 5000
})

// Query event history
MATCH (a:Account {id: 'A001'})-[:HAS_EVENT]->(e:AccountEvent)
RETURN e
ORDER BY e.timestamp DESC

// Reconstruct state at a point in time
MATCH (a:Account {id: 'A001'})-[:HAS_EVENT]->(e:AccountEvent)
WHERE e.timestamp <= datetime('2026-01-01T00:00:00Z')
WITH e ORDER BY e.timestamp DESC LIMIT 1
RETURN e.balance AS balanceAtDate
```

### Temporal Versioning

Keep history of entity changes:

```cypher
// Version chain pattern
(:Product {sku: 'SKU001'})-[:CURRENT_VERSION]->(:ProductVersion {
    version: 3,
    name: 'Widget Pro',
    price: 29.99,
    validFrom: datetime('2026-01-01'),
    validTo: null
})

(:Product)-[:HAS_VERSION]->(:ProductVersion {
    version: 2,
    name: 'Widget',
    price: 24.99,
    validFrom: datetime('2025-06-01'),
    validTo: datetime('2025-12-31')
})

// Query current state
MATCH (p:Product {sku: 'SKU001'})-[:CURRENT_VERSION]->(v:ProductVersion)
RETURN v.name, v.price

// Query state at specific time
MATCH (p:Product {sku: 'SKU001'})-[:HAS_VERSION]->(v:ProductVersion)
WHERE v.validFrom <= datetime('2025-09-01') 
  AND (v.validTo IS NULL OR v.validTo > datetime('2025-09-01'))
RETURN v.name, v.price
```

### Bitemporal Pattern

Track both valid time and transaction time:

```cypher
(:Entity)-[:HAS_STATE]->(:EntityState {
    // What was recorded
    data: '...',
    
    // When it was true in the real world
    validFrom: date('2026-01-01'),
    validTo: date('2026-12-31'),
    
    // When we recorded it in the system
    recordedAt: datetime('2026-01-15T10:30:00Z'),
    supersededAt: null  // null means current record
})
```

### Time Trees

For efficient time-based queries:

```cypher
// Year -> Month -> Day hierarchy
(:Year {year: 2026})-[:HAS_MONTH]->(:Month {month: 1})-[:HAS_DAY]->(:Day {day: 25})

// Connect events to time tree
(:Event)-[:OCCURRED_ON]->(:Day)

// Query all events in January 2026
MATCH (:Year {year: 2026})-[:HAS_MONTH]->(:Month {month: 1})-[:HAS_DAY]->(d:Day)
MATCH (e:Event)-[:OCCURRED_ON]->(d)
RETURN e
```

---

## 15.3 Linked List Pattern

### Sequential Data

When order matters and you need to traverse sequentially:

```cypher
// Playlist songs
(:Playlist {name: 'My Favorites'})
    -[:FIRST_TRACK]->(:Track {title: 'Song A'})
    -[:NEXT]->(:Track {title: 'Song B'})
    -[:NEXT]->(:Track {title: 'Song C'})

// Process chain
(:Workflow)-[:FIRST_STEP]->(:Step {name: 'Review'})
    -[:NEXT_STEP]->(:Step {name: 'Approve'})
    -[:NEXT_STEP]->(:Step {name: 'Execute'})

// Query full sequence
MATCH (p:Playlist {name: 'My Favorites'})-[:FIRST_TRACK]->(first:Track)
MATCH path = (first)-[:NEXT*0..]->(track:Track)
RETURN [t IN nodes(path) | t.title] AS trackOrder
```

### Doubly Linked List

For bidirectional traversal:

```cypher
// Create with NEXT and PREV
(:Step {order: 1})-[:NEXT]->(:Step {order: 2})-[:NEXT]->(:Step {order: 3})
(:Step {order: 3})-[:PREV]->(:Step {order: 2})-[:PREV]->(:Step {order: 1})

// Or use single relationship queried both ways
(:Step {order: 1})-[:ADJACENT]->(:Step {order: 2})-[:ADJACENT]->(:Step {order: 3})
```

---

## 15.4 Tree and Hierarchy Patterns

### Adjacency List (Simple Parent-Child)

```cypher
// Organization structure
(:Employee {name: 'CEO'})<-[:REPORTS_TO]-(:Employee {name: 'VP Sales'})
(:Employee {name: 'VP Sales'})<-[:REPORTS_TO]-(:Employee {name: 'Sales Manager'})

// Find all reports (direct and indirect)
MATCH (ceo:Employee {name: 'CEO'})<-[:REPORTS_TO*]-(report:Employee)
RETURN report.name, length(shortestPath((report)-[:REPORTS_TO*]->(ceo))) AS level

// Find reporting chain
MATCH path = (emp:Employee {name: 'Sales Rep'})-[:REPORTS_TO*]->(top:Employee)
WHERE NOT (top)-[:REPORTS_TO]->()
RETURN [n IN nodes(path) | n.name] AS chain
```

### Materialized Path

Store the full path for fast ancestor queries:

```cypher
// Category with path
(:Category {
    name: 'Laptops',
    path: '/Electronics/Computers/Laptops',
    level: 3
})

// Find all ancestors
MATCH (c:Category {name: 'Laptops'})
WITH split(c.path, '/') AS pathParts
UNWIND range(1, size(pathParts)-1) AS i
WITH [p IN pathParts[1..i+1] | p] AS ancestorPath
MATCH (ancestor:Category)
WHERE ancestor.path = '/' + apoc.text.join(ancestorPath, '/')
RETURN ancestor.name

// Find all descendants
MATCH (c:Category)
WHERE c.path STARTS WITH '/Electronics/Computers'
RETURN c.name
```

### Nested Set Model

For efficient subtree queries:

```cypher
// Category with left/right bounds
(:Category {name: 'Electronics', lft: 1, rgt: 10})
(:Category {name: 'Computers', lft: 2, rgt: 7})
(:Category {name: 'Laptops', lft: 3, rgt: 4})
(:Category {name: 'Desktops', lft: 5, rgt: 6})
(:Category {name: 'Phones', lft: 8, rgt: 9})

// Find all descendants
MATCH (parent:Category {name: 'Electronics'}), (child:Category)
WHERE child.lft > parent.lft AND child.rgt < parent.rgt
RETURN child.name

// Find all ancestors
MATCH (child:Category {name: 'Laptops'}), (ancestor:Category)
WHERE ancestor.lft < child.lft AND ancestor.rgt > child.rgt
RETURN ancestor.name
```

---

## 15.5 Access Control Patterns

### Role-Based Access Control (RBAC)

```cypher
// Structure
(:User)-[:HAS_ROLE]->(:Role)-[:HAS_PERMISSION]->(:Permission)
(:Permission)-[:ON_RESOURCE]->(:Resource)

// Example
CREATE (u:User {name: 'Alice'})
CREATE (r:Role {name: 'Editor'})
CREATE (p:Permission {action: 'WRITE'})
CREATE (res:Resource {type: 'Document'})
CREATE (u)-[:HAS_ROLE]->(r)
CREATE (r)-[:HAS_PERMISSION]->(p)
CREATE (p)-[:ON_RESOURCE]->(res)

// Check permission
MATCH (u:User {name: 'Alice'})-[:HAS_ROLE]->(:Role)-[:HAS_PERMISSION]->(p:Permission)-[:ON_RESOURCE]->(r:Resource)
WHERE p.action = 'WRITE' AND r.type = 'Document'
RETURN count(*) > 0 AS hasPermission
```

### Attribute-Based Access Control (ABAC)

```cypher
// Document with security attributes
(:Document {
    id: 'D001',
    classification: 'Confidential',
    department: 'Finance'
})

// User with clearance
(:User {
    name: 'Alice',
    clearanceLevel: 'Secret',
    departments: ['Finance', 'HR']
})

// Check access
MATCH (u:User {name: 'Alice'}), (d:Document {id: 'D001'})
WHERE d.department IN u.departments
  AND (d.classification = 'Public' 
       OR (d.classification = 'Confidential' AND u.clearanceLevel IN ['Confidential', 'Secret', 'TopSecret'])
       OR (d.classification = 'Secret' AND u.clearanceLevel IN ['Secret', 'TopSecret']))
RETURN d
```

### Graph-Based Access Control

```cypher
// Access through organizational hierarchy
(:User)-[:MEMBER_OF]->(:Team)-[:PART_OF]->(:Department)-[:OWNS]->(:Resource)

// Check if user can access resource
MATCH (u:User {name: 'Alice'})-[:MEMBER_OF|MANAGES*1..5]->(team)
MATCH (team)-[:PART_OF*0..3]->(dept)-[:OWNS]->(r:Resource {id: 'R001'})
RETURN count(*) > 0 AS hasAccess
```

---

## 15.6 Recommendation Patterns

### Collaborative Filtering

```cypher
// Users who bought X also bought Y
MATCH (target:Customer {id: $customerId})-[:PURCHASED]->(p:Product)
MATCH (other:Customer)-[:PURCHASED]->(p)
MATCH (other)-[:PURCHASED]->(rec:Product)
WHERE NOT (target)-[:PURCHASED]->(rec)
RETURN rec.name, count(DISTINCT other) AS score
ORDER BY score DESC
LIMIT 10

// Content-based: Similar products by category/attributes
MATCH (p:Product {id: $productId})-[:IN_CATEGORY]->(cat:Category)
MATCH (similar:Product)-[:IN_CATEGORY]->(cat)
WHERE similar <> p
RETURN similar.name, count(cat) AS commonCategories
ORDER BY commonCategories DESC
```

### Friend Suggestions

```cypher
// Friends of friends
MATCH (me:Person {id: $userId})-[:FRIENDS_WITH]->(friend)-[:FRIENDS_WITH]->(suggestion:Person)
WHERE NOT (me)-[:FRIENDS_WITH]->(suggestion)
  AND me <> suggestion
RETURN suggestion.name, count(friend) AS mutualFriends
ORDER BY mutualFriends DESC
LIMIT 10

// Similar interests
MATCH (me:Person {id: $userId})-[:INTERESTED_IN]->(interest:Topic)
MATCH (suggestion:Person)-[:INTERESTED_IN]->(interest)
WHERE NOT (me)-[:FRIENDS_WITH]->(suggestion)
  AND me <> suggestion
RETURN suggestion.name, collect(interest.name) AS commonInterests, count(interest) AS score
ORDER BY score DESC
LIMIT 10
```

---

## 15.7 Multi-Tenancy Patterns

### Tenant as Property

Simple but limited:

```cypher
// All nodes have tenantId
(:Customer {tenantId: 'T001', name: 'Alice'})
(:Order {tenantId: 'T001', id: 'O001'})

// Always filter by tenant
MATCH (c:Customer {tenantId: $tenantId})-[:PLACED]->(o:Order {tenantId: $tenantId})
RETURN c, o
```

### Tenant as Node

More flexible:

```cypher
// Tenant node connected to all owned data
(:Tenant {id: 'T001', name: 'Acme Corp'})
    -[:OWNS]->(:Customer {name: 'Alice'})
    -[:PLACED]->(:Order {id: 'O001'})

// Query within tenant
MATCH (t:Tenant {id: $tenantId})-[:OWNS]->(c:Customer)-[:PLACED]->(o:Order)
RETURN c.name, o.id

// Share data between tenants
(:Tenant {id: 'T001'})-[:CAN_ACCESS]->(:SharedResource)<-[:CAN_ACCESS]-(:Tenant {id: 'T002'})
```

### Separate Databases

For complete isolation, use separate Neo4j databases per tenant (Enterprise Edition).

---

## 15.8 Graph-Specific Patterns

### Hyperedges

When a relationship connects more than two nodes:

```cypher
// Meeting involves multiple people
(:Meeting {
    title: 'Project Review',
    date: date('2026-01-25')
})
(:Person)-[:ATTENDED {role: 'organizer'}]->(:Meeting)
(:Person)-[:ATTENDED {role: 'participant'}]->(:Meeting)
(:Person)-[:ATTENDED {role: 'participant'}]->(:Meeting)

// Query meeting participants
MATCH (m:Meeting {title: 'Project Review'})<-[a:ATTENDED]-(p:Person)
RETURN p.name, a.role
```

### Faceted Classification

Items belonging to multiple overlapping categories:

```cypher
// Product with multiple facets
(:Product {name: 'Running Shoes'})
    -[:HAS_BRAND]->(:Brand {name: 'Nike'})
    -[:HAS_COLOR]->(:Color {name: 'Red'})
    -[:HAS_SIZE]->(:Size {value: '10'})
    -[:FOR_ACTIVITY]->(:Activity {name: 'Running'})
    -[:FOR_GENDER]->(:Gender {name: 'Men'})

// Faceted search
MATCH (p:Product)
WHERE EXISTS { (p)-[:HAS_BRAND]->(:Brand {name: 'Nike'}) }
  AND EXISTS { (p)-[:FOR_ACTIVITY]->(:Activity {name: 'Running'}) }
  AND EXISTS { (p)-[:HAS_SIZE]->(:Size {value: '10'}) }
RETURN p.name
```

### Knowledge Graph Pattern

Flexible schema for diverse knowledge:

```cypher
// Generic triple pattern
(:Entity {name: 'Albert Einstein', type: 'Person'})
    -[:RELATION {type: 'bornIn'}]->
(:Entity {name: 'Ulm', type: 'City'})

// Or strongly typed
(:Person {name: 'Albert Einstein'})-[:BORN_IN]->(:City {name: 'Ulm'})
(:Person {name: 'Albert Einstein'})-[:DEVELOPED]->(:Theory {name: 'Relativity'})
(:Theory {name: 'Relativity'})-[:FIELD]->(:Science {name: 'Physics'})

// Query knowledge
MATCH (e:Person {name: 'Albert Einstein'})-[r]->(related)
RETURN type(r) AS relationship, labels(related)[0] AS relatedType, related.name
```

---

## 15.9 Python Implementation Examples

```python
from neo4j import GraphDatabase
from datetime import datetime, date

URI = "neo4j://localhost:7687"
AUTH = ("neo4j", "password")

class GraphPatterns:
    def __init__(self, uri, auth):
        self.driver = GraphDatabase.driver(uri, auth=auth)
    
    def close(self):
        self.driver.close()
    
    # Intermediate Node Pattern
    def create_employment(self, person_id: str, company_id: str, 
                          title: str, department_id: str, start_date: date):
        with self.driver.session() as session:
            return session.run("""
                MATCH (p:Person {id: $personId})
                MATCH (c:Company {id: $companyId})
                MATCH (d:Department {id: $deptId})
                CREATE (e:Employment {
                    title: $title,
                    startDate: $startDate,
                    createdAt: datetime()
                })
                CREATE (p)-[:HAS_EMPLOYMENT]->(e)
                CREATE (e)-[:AT_COMPANY]->(c)
                CREATE (e)-[:IN_DEPARTMENT]->(d)
                RETURN e
            """, personId=person_id, companyId=company_id,
                title=title, deptId=department_id, startDate=start_date).single()
    
    # Time-based versioning
    def update_product_with_history(self, sku: str, new_data: dict):
        with self.driver.session() as session:
            return session.run("""
                MATCH (p:Product {sku: $sku})-[cur:CURRENT_VERSION]->(oldVersion:ProductVersion)
                
                // Close out old version
                SET oldVersion.validTo = datetime()
                DELETE cur
                
                // Create new version
                CREATE (newVersion:ProductVersion {
                    version: oldVersion.version + 1,
                    name: $name,
                    price: $price,
                    validFrom: datetime(),
                    validTo: null
                })
                CREATE (p)-[:CURRENT_VERSION]->(newVersion)
                CREATE (p)-[:HAS_VERSION]->(newVersion)
                
                RETURN newVersion
            """, sku=sku, **new_data).single()
    
    # Collaborative filtering recommendation
    def get_recommendations(self, customer_id: str, limit: int = 10):
        with self.driver.session() as session:
            result = session.run("""
                MATCH (target:Customer {id: $customerId})-[:PURCHASED]->(p:Product)
                MATCH (other:Customer)-[:PURCHASED]->(p)
                WHERE other <> target
                MATCH (other)-[:PURCHASED]->(rec:Product)
                WHERE NOT (target)-[:PURCHASED]->(rec)
                WITH rec, count(DISTINCT other) AS score
                RETURN rec.name AS product, rec.sku, score
                ORDER BY score DESC
                LIMIT $limit
            """, customerId=customer_id, limit=limit)
            
            return [dict(r) for r in result]
    
    # Access control check
    def check_permission(self, user_id: str, action: str, resource_type: str) -> bool:
        with self.driver.session() as session:
            result = session.run("""
                MATCH (u:User {id: $userId})
                      -[:HAS_ROLE]->(:Role)
                      -[:HAS_PERMISSION]->(p:Permission {action: $action})
                      -[:ON_RESOURCE]->(:Resource {type: $resourceType})
                RETURN count(*) > 0 AS hasPermission
            """, userId=user_id, action=action, resourceType=resource_type)
            
            return result.single()['hasPermission']

# Usage
patterns = GraphPatterns(URI, AUTH)
try:
    # Get recommendations
    recs = patterns.get_recommendations('C001')
    for rec in recs:
        print(f"{rec['product']}: score {rec['score']}")
    
    # Check permission
    can_write = patterns.check_permission('U001', 'WRITE', 'Document')
    print(f"Can write documents: {can_write}")
finally:
    patterns.close()
```

---

## Summary

### Pattern Catalog

| Pattern | Use Case |
|---------|----------|
| **Intermediate Node** | Relationship needs connections to other nodes |
| **Event Sourcing** | Track all state changes |
| **Temporal Versioning** | History with point-in-time queries |
| **Linked List** | Ordered sequences |
| **Tree/Hierarchy** | Parent-child structures |
| **RBAC/ABAC** | Access control |
| **Collaborative Filtering** | Recommendations |
| **Multi-Tenancy** | Data isolation between clients |
| **Hyperedge** | N-ary relationships |
| **Knowledge Graph** | Flexible domain modeling |

---

## Exercises

### Exercise 15.1: Event Sourcing
Design and implement an event-sourced bank account with:
- Deposits and withdrawals
- Balance calculation from events
- Statement generation for date range

### Exercise 15.2: Versioned Content
Create a document management system with:
- Version history
- Branching (like git)
- Diff between versions

### Exercise 15.3: Recommendations
Build a recommendation engine for:
- Products based on purchase history
- Content based on viewing history
- Hybrid approach combining both

### Exercise 15.4: Access Control
Implement a complete RBAC system with:
- Users, roles, permissions
- Resource-level permissions
- Permission inheritance through role hierarchy

---

**Next Chapter: [Chapter 16: Data Modeling Anti-Patterns](16-data-modeling-antipatterns.md)**
