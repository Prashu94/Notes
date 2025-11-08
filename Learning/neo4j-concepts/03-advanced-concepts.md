# Advanced Neo4j Concepts

## Table of Contents
1. [Indexes](#indexes)
2. [Constraints](#constraints)
3. [Transactions](#transactions)
4. [Graph Algorithms](#graph-algorithms)
5. [Performance Optimization](#performance-optimization)
6. [Full-Text Search](#full-text-search)
7. [Vector Indexes (AI/ML)](#vector-indexes-aiml)
8. [Import/Export Data](#importexport-data)
9. [Best Practices](#best-practices)

---

## Indexes

Indexes significantly improve query performance for property lookups and pattern matching.

### Types of Indexes

#### 1. B-tree Index (Range Index)

Default index type for property lookups.

```cypher
// Create single-property index
CREATE INDEX person_name_idx FOR (p:Person) ON (p.name)

// Create composite index (multiple properties)
CREATE INDEX person_name_age_idx FOR (p:Person) ON (p.name, p.age)

// Create index on relationship property
CREATE INDEX worked_for_since_idx FOR ()-[r:WORKS_FOR]-() ON (r.since)
```

#### 2. Text Index

For string prefix, suffix, and substring searches.

```cypher
// Create text index
CREATE TEXT INDEX person_email_text_idx FOR (p:Person) ON (p.email)

// Use with CONTAINS, STARTS WITH, ENDS WITH
MATCH (p:Person)
WHERE p.email CONTAINS "@gmail.com"
RETURN p.name, p.email
```

#### 3. Point Index

For spatial/geographical queries.

```cypher
// Create point index
CREATE POINT INDEX location_coordinates_idx FOR (l:Location) ON (l.coordinates)

// Query by distance
MATCH (l:Location)
WHERE point.distance(l.coordinates, point({latitude: 37.7749, longitude: -122.4194})) < 10000
RETURN l.name, l.coordinates
```

#### 4. Full-Text Index

For complex text search with scoring and relevance.

```cypher
// Create full-text index
CREATE FULLTEXT INDEX person_search_idx FOR (p:Person) ON EACH [p.name, p.bio, p.interests]

// Search using full-text
CALL db.index.fulltext.queryNodes("person_search_idx", "software engineer python")
YIELD node, score
RETURN node.name, node.bio, score
ORDER BY score DESC
LIMIT 10
```

#### 5. Vector Index (for AI/ML embeddings)

```cypher
// Create vector index for embeddings
CREATE VECTOR INDEX document_embeddings_idx FOR (d:Document) ON (d.embedding)
OPTIONS {indexConfig: {
    `vector.dimensions`: 1536,
    `vector.similarity_function`: 'cosine'
}}

// Query similar vectors
MATCH (d:Document)
WHERE d.embedding IS NOT NULL
CALL db.index.vector.queryNodes('document_embeddings_idx', 10, $queryEmbedding)
YIELD node, score
RETURN node.title, score
```

### Managing Indexes

```cypher
// List all indexes
SHOW INDEXES

// Show specific index details
SHOW INDEX YIELD *
WHERE name = "person_name_idx"

// Drop index
DROP INDEX person_name_idx

// Check if index exists
SHOW INDEXES
WHERE name = "person_name_idx"
```

### Index Usage Tips

1. **Index selective properties**: Index properties used frequently in WHERE clauses
2. **Composite indexes**: Order matters - most selective property first
3. **Monitor usage**: Use PROFILE to see if indexes are used
4. **Don't over-index**: Each index adds write overhead

```cypher
// Check if query uses index
PROFILE
MATCH (p:Person {name: "Alice"})
RETURN p
```

---

## Constraints

Constraints enforce data integrity rules.

### Types of Constraints

#### 1. Unique Constraint

Ensures property values are unique across nodes.

```cypher
// Unique constraint (automatically creates index)
CREATE CONSTRAINT person_email_unique FOR (p:Person) REQUIRE p.email IS UNIQUE

// Composite unique constraint
CREATE CONSTRAINT person_firstname_lastname_unique 
FOR (p:Person) REQUIRE (p.firstName, p.lastName) IS UNIQUE

// Attempt to violate will fail
CREATE (:Person {email: "alice@example.com"})  // OK
CREATE (:Person {email: "alice@example.com"})  // ERROR: Already exists
```

#### 2. Node Key Constraint

Ensures combination of properties exists and is unique (Enterprise only).

```cypher
// Node key constraint
CREATE CONSTRAINT person_id_key FOR (p:Person) REQUIRE (p.personId) IS NODE KEY

// Composite node key
CREATE CONSTRAINT product_sku_key 
FOR (p:Product) REQUIRE (p.sku, p.version) IS NODE KEY
```

#### 3. Property Existence Constraint

Ensures property must exist (Enterprise only).

```cypher
// Property must exist
CREATE CONSTRAINT person_name_exists FOR (p:Person) REQUIRE p.name IS NOT NULL

// On relationships
CREATE CONSTRAINT worked_since_exists 
FOR ()-[r:WORKS_FOR]-() REQUIRE r.since IS NOT NULL
```

#### 4. Property Type Constraint

Ensures property has specific type (Neo4j 5.0+).

```cypher
// Type constraint
CREATE CONSTRAINT person_age_type FOR (p:Person) REQUIRE p.age IS :: INTEGER

// Multiple types
CREATE CONSTRAINT person_id_type FOR (p:Person) REQUIRE p.id IS :: STRING | INTEGER
```

### Managing Constraints

```cypher
// List all constraints
SHOW CONSTRAINTS

// Drop constraint
DROP CONSTRAINT person_email_unique

// Show constraint details
SHOW CONSTRAINT YIELD *
WHERE name = "person_email_unique"
```

---

## Transactions

Neo4j is fully ACID compliant with transaction support.

### Transaction Basics

```cypher
// Auto-commit transaction (single statement)
CREATE (:Person {name: "Alice"})

// All Cypher statements in a query run in one transaction
CREATE (:Person {name: "Alice"})
CREATE (:Person {name: "Bob"})
MATCH (a:Person {name: "Alice"}), (b:Person {name: "Bob"})
CREATE (a)-[:FRIENDS_WITH]->(b)
// All succeed or all fail together
```

### Explicit Transactions (Neo4j Browser)

```cypher
:begin
CREATE (:Person {name: "Alice"})
CREATE (:Person {name: "Bob"})
:commit

// Or rollback
:begin
CREATE (:Person {name: "Charlie"})
:rollback  // Changes discarded
```

### Transaction Functions (Python Driver)

See Python implementation section for detailed examples with:
- `session.execute_write()`
- `session.execute_read()`
- Manual transaction management with `session.begin_transaction()`

### Transaction Best Practices

1. **Keep transactions short**: Long transactions lock resources
2. **Batch large imports**: Use periodic commits
3. **Read vs Write transactions**: Use read transactions when possible
4. **Handle failures**: Implement retry logic for transient errors

```cypher
// Periodic commit for large imports (deprecated in Neo4j 5.0+)
// Use CALL {} IN TRANSACTIONS instead
LOAD CSV FROM "file:///large_dataset.csv" AS row
CALL {
    WITH row
    CREATE (:Person {name: row.name, age: toInteger(row.age)})
} IN TRANSACTIONS OF 1000 ROWS
```

---

## Graph Algorithms

Neo4j Graph Data Science (GDS) library provides powerful algorithms.

### Setup GDS

```cypher
// Check if GDS is installed
CALL gds.version()

// List available algorithms
CALL gds.list()
```

### Common Algorithms

#### 1. PageRank (Importance/Influence)

```cypher
// Create graph projection
CALL gds.graph.project(
    'socialNetwork',
    'Person',
    'FOLLOWS'
)

// Run PageRank
CALL gds.pageRank.stream('socialNetwork')
YIELD nodeId, score
RETURN gds.util.asNode(nodeId).name AS person, score
ORDER BY score DESC
LIMIT 10
```

#### 2. Community Detection (Louvain)

```cypher
// Find communities/clusters
CALL gds.louvain.stream('socialNetwork')
YIELD nodeId, communityId
RETURN communityId, collect(gds.util.asNode(nodeId).name) AS members, count(*) AS size
ORDER BY size DESC
```

#### 3. Shortest Path (Dijkstra)

```cypher
// Find shortest weighted path
MATCH (start:Person {name: "Alice"}), (end:Person {name: "Bob"})
CALL gds.shortestPath.dijkstra.stream('socialNetwork', {
    sourceNode: start,
    targetNode: end,
    relationshipWeightProperty: 'weight'
})
YIELD nodeIds, totalCost
RETURN [nodeId IN nodeIds | gds.util.asNode(nodeId).name] AS path, totalCost
```

#### 4. Node Similarity

```cypher
// Find similar nodes based on relationships
CALL gds.nodeSimilarity.stream('socialNetwork')
YIELD node1, node2, similarity
RETURN gds.util.asNode(node1).name AS person1, 
       gds.util.asNode(node2).name AS person2, 
       similarity
ORDER BY similarity DESC
LIMIT 10
```

#### 5. Centrality Algorithms

```cypher
// Degree Centrality (number of connections)
CALL gds.degree.stream('socialNetwork')
YIELD nodeId, score
RETURN gds.util.asNode(nodeId).name AS person, score
ORDER BY score DESC

// Betweenness Centrality (bridge nodes)
CALL gds.betweenness.stream('socialNetwork')
YIELD nodeId, score
RETURN gds.util.asNode(nodeId).name AS person, score
ORDER BY score DESC
```

### Cleanup

```cypher
// Drop graph projection when done
CALL gds.graph.drop('socialNetwork')
```

---

## Performance Optimization

### Query Optimization Techniques

#### 1. Use PROFILE and EXPLAIN

```cypher
// See query execution plan
EXPLAIN
MATCH (p:Person)-[:FRIENDS_WITH]->(friend)
WHERE p.name = "Alice"
RETURN friend.name

// See actual execution metrics
PROFILE
MATCH (p:Person)-[:FRIENDS_WITH]->(friend)
WHERE p.name = "Alice"
RETURN friend.name
```

#### 2. Use Parameters

```cypher
// Bad - query cache miss for each different value
MATCH (p:Person {name: "Alice"})
RETURN p

// Good - parameterized query
MATCH (p:Person {name: $name})
RETURN p
```

#### 3. Limit Early

```cypher
// Bad - processes all results then limits
MATCH (p:Person)
WITH p
ORDER BY p.age DESC
LIMIT 10
RETURN p.name, p.age

// Good - limits during processing
MATCH (p:Person)
RETURN p.name, p.age
ORDER BY p.age DESC
LIMIT 10
```

#### 4. Use Indexes

```cypher
// Create index
CREATE INDEX person_name_idx FOR (p:Person) ON (p.name)

// Query uses index
MATCH (p:Person {name: $name})
RETURN p
// or
MATCH (p:Person)
WHERE p.name = $name
RETURN p
```

#### 5. Avoid Cartesian Products

```cypher
// Bad - creates all combinations
MATCH (p:Person), (c:Company)
WHERE p.name = "Alice" AND c.name = "TechCorp"
CREATE (p)-[:WORKS_FOR]->(c)

// Good - connect patterns
MATCH (p:Person {name: "Alice"}), (c:Company {name: "TechCorp"})
CREATE (p)-[:WORKS_FOR]->(c)
```

#### 6. Use WITH for Complex Queries

```cypher
// Break complex queries into steps
MATCH (p:Person)
WHERE p.age > 25
WITH p
MATCH (p)-[:WORKS_FOR]->(c:Company)
WITH p, c, count(*) AS jobCount
WHERE jobCount > 2
RETURN p.name, jobCount
```

### Database Configuration

```cypher
// Check configuration
CALL dbms.listConfig()
YIELD name, value
WHERE name STARTS WITH 'dbms.memory'
RETURN name, value

// Key settings (set in neo4j.conf):
// dbms.memory.heap.initial_size=1g
// dbms.memory.heap.max_size=4g
// dbms.memory.pagecache.size=4g
```

### Monitoring

```cypher
// Current queries
CALL dbms.listQueries()
YIELD queryId, query, elapsedTimeMillis, status
WHERE elapsedTimeMillis > 1000
RETURN queryId, query, elapsedTimeMillis
ORDER BY elapsedTimeMillis DESC

// Kill long-running query
CALL dbms.killQuery("query-123")

// Database statistics
CALL apoc.meta.stats()
YIELD nodeCount, relCount, labelCount
RETURN nodeCount, relCount, labelCount
```

---

## Full-Text Search

### Creating Full-Text Indexes

```cypher
// Create full-text index on multiple properties
CREATE FULLTEXT INDEX article_content_idx 
FOR (a:Article) 
ON EACH [a.title, a.content, a.summary]

// On multiple labels
CREATE FULLTEXT INDEX content_search_idx 
FOR (n:Article|BlogPost|Document) 
ON EACH [n.title, n.content]

// On relationships
CREATE FULLTEXT INDEX review_text_idx 
FOR ()-[r:REVIEWED]-() 
ON EACH [r.text, r.summary]
```

### Querying Full-Text Indexes

```cypher
// Basic search
CALL db.index.fulltext.queryNodes("article_content_idx", "machine learning")
YIELD node, score
RETURN node.title, node.content, score
ORDER BY score DESC
LIMIT 10

// Advanced search syntax
CALL db.index.fulltext.queryNodes("article_content_idx", 
    "machine AND learning AND (python OR java)")
YIELD node, score
RETURN node.title, score

// Fuzzy search (tolerance for typos)
CALL db.index.fulltext.queryNodes("article_content_idx", "machne~")
YIELD node, score
RETURN node.title, score

// Phrase search
CALL db.index.fulltext.queryNodes("article_content_idx", '"artificial intelligence"')
YIELD node, score
RETURN node.title, score

// Wildcard search
CALL db.index.fulltext.queryNodes("article_content_idx", "mach*")
YIELD node, score
RETURN node.title, score
```

### Full-Text Search Options

```cypher
// Create with custom analyzer
CREATE FULLTEXT INDEX article_content_custom_idx 
FOR (a:Article) 
ON EACH [a.content]
OPTIONS {
    indexConfig: {
        `fulltext.analyzer`: 'english',
        `fulltext.eventually_consistent`: true
    }
}

// Available analyzers: standard, simple, whitespace, english, swedish, etc.
```

---

## Vector Indexes (AI/ML)

Vector indexes enable similarity search for AI/ML applications, especially RAG systems.

### Creating Vector Indexes

```cypher
// Create vector index for document embeddings
CREATE VECTOR INDEX document_embeddings 
FOR (d:Document) 
ON (d.embedding)
OPTIONS {
    indexConfig: {
        `vector.dimensions`: 1536,              // OpenAI ada-002: 1536
        `vector.similarity_function`: 'cosine'  // cosine, euclidean, or dot product
    }
}

// For different embedding models:
// - OpenAI text-embedding-ada-002: 1536 dimensions
// - OpenAI text-embedding-3-small: 1536 dimensions  
// - OpenAI text-embedding-3-large: 3072 dimensions
// - Sentence-Transformers: 384-768 dimensions
```

### Querying Vector Indexes

```cypher
// Similarity search
MATCH (d:Document)
WHERE d.embedding IS NOT NULL
CALL db.index.vector.queryNodes('document_embeddings', 10, $queryEmbedding)
YIELD node, score
RETURN node.title, node.content, score
ORDER BY score DESC

// Hybrid search (vector + property filters)
MATCH (d:Document)
WHERE d.category = "technology" AND d.embedding IS NOT NULL
CALL db.index.vector.queryNodes('document_embeddings', 5, $queryEmbedding)
YIELD node, score
WHERE score > 0.8
RETURN node.title, node.content, score
```

### Vector Index Management

```cypher
// Show vector indexes
SHOW INDEXES
WHERE type = "VECTOR"

// Drop vector index
DROP INDEX document_embeddings
```

---

## Import/Export Data

### CSV Import

```cypher
// Load CSV (file must be in import directory)
LOAD CSV WITH HEADERS FROM 'file:///people.csv' AS row
CREATE (:Person {
    name: row.name,
    age: toInteger(row.age),
    email: row.email
})

// Load from URL
LOAD CSV WITH HEADERS FROM 'https://example.com/data.csv' AS row
CREATE (:Person {name: row.name, age: toInteger(row.age)})

// Batch processing (Neo4j 5.0+)
LOAD CSV WITH HEADERS FROM 'file:///large_file.csv' AS row
CALL {
    WITH row
    MERGE (p:Person {email: row.email})
    SET p.name = row.name, p.age = toInteger(row.age)
} IN TRANSACTIONS OF 1000 ROWS
```

### APOC Import/Export

```cypher
// Export to CSV
CALL apoc.export.csv.query(
    "MATCH (p:Person) RETURN p.name AS name, p.age AS age",
    "people_export.csv",
    {}
)

// Export to JSON
CALL apoc.export.json.all("full_database.json", {})

// Import JSON
CALL apoc.load.json("file:///data.json") YIELD value
UNWIND value.people AS person
CREATE (:Person {name: person.name, age: person.age})

// Import from relational database
CALL apoc.load.jdbc(
    "jdbc:mysql://localhost:3306/mydb",
    "SELECT * FROM people"
) YIELD row
CREATE (:Person {name: row.name, age: row.age})
```

### Backup and Restore

```bash
# Backup (command line)
neo4j-admin database dump neo4j --to-path=/backups

# Restore
neo4j-admin database load neo4j --from-path=/backups/neo4j.dump
```

---

## Best Practices

### Data Modeling

1. **Model for queries**: Design based on how you'll query data
2. **Use meaningful labels**: `:Person`, `:Product` not `:Node1`
3. **Use descriptive relationships**: `:FRIENDS_WITH`, `:PURCHASED` not `:RELATED_TO`
4. **Denormalize when needed**: Add redundant properties for performance
5. **Avoid dense nodes**: Node with millions of relationships (use intermediate nodes)

### Query Best Practices

1. **Use parameters**: Improves query caching
2. **Profile queries**: Understand execution plans
3. **Limit results**: Always use LIMIT in exploration
4. **Use indexes**: Index frequently queried properties
5. **Avoid (\*) patterns**: Be specific about labels and relationships
6. **Use MERGE carefully**: Can create duplicates if pattern isn't unique

### Performance

1. **Batch writes**: Process in transactions of 500-10,000 rows
2. **Use APOC**: Extended functionality and better performance
3. **Monitor memory**: Adjust heap and page cache
4. **Optimize traversals**: Use OPTIONAL MATCH wisely
5. **Consider sharding**: For very large graphs (Enterprise)

### Security

```cypher
// Create user
CREATE USER alice SET PASSWORD 'secure_password';

// Grant privileges
GRANT ROLE reader TO alice;
GRANT MATCH {*} ON GRAPH neo4j TO alice;

// Create custom role
CREATE ROLE analyst;
GRANT MATCH {*} ON GRAPH neo4j NODES Person, Company TO analyst;
GRANT CREATE ON GRAPH neo4j NODES Report TO analyst;
```

### Maintenance

```cypher
// Check database info
CALL db.info()

// Schema information
CALL db.schema.visualization()

// Count nodes and relationships
MATCH (n) RETURN count(n) AS nodeCount;
MATCH ()-[r]->() RETURN count(r) AS relationshipCount;

// Find disconnected nodes
MATCH (n)
WHERE NOT (n)--()
RETURN labels(n), count(n)
```

---

## Common Pitfalls to Avoid

1. **Creating duplicate nodes**: Always use MERGE with unique properties
2. **Missing indexes**: Queries on large datasets without indexes
3. **Cartesian products**: Unconnected MATCH clauses
4. **Unbounded variable-length paths**: Use upper limit `[:REL*1..5]`
5. **Not using parameters**: Impacts query cache
6. **Over-fetching data**: Return only what you need
7. **Ignoring PROFILE output**: Not monitoring performance

---

## Quick Command Reference

```cypher
// Indexes
CREATE INDEX idx_name FOR (n:Label) ON (n.property)
SHOW INDEXES
DROP INDEX idx_name

// Constraints
CREATE CONSTRAINT cons_name FOR (n:Label) REQUIRE n.property IS UNIQUE
SHOW CONSTRAINTS
DROP CONSTRAINT cons_name

// Transactions
:begin
// queries
:commit  // or :rollback

// Performance
EXPLAIN query...
PROFILE query...

// Algorithms
CALL gds.graph.project(...)
CALL gds.pageRank.stream(...)
CALL gds.graph.drop(...)
```

---

**Next:** Proceed to [04-python-neo4j-basics.md](04-python-neo4j-basics.md) to start implementing Neo4j with Python.
