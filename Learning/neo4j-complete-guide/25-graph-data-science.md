# Chapter 25: Graph Data Science Library

## Learning Objectives
By the end of this chapter, you will:
- Install and configure the Graph Data Science (GDS) library
- Create and manage graph projections
- Run graph algorithms efficiently
- Write results back to the database
- Integrate GDS with Python applications

---

## 25.1 Introduction to Graph Data Science

### What is GDS?

The Neo4j Graph Data Science library provides graph algorithms for:
- **Centrality**: Find important nodes
- **Community Detection**: Discover clusters
- **Similarity**: Find similar nodes
- **Path Finding**: Optimal routes
- **Link Prediction**: Predict future connections
- **Node Embedding**: Vector representations

### Installing GDS

```bash
# Download GDS plugin from Neo4j Download Center
# Place in /plugins directory

# Configure neo4j.conf
dbms.security.procedures.unrestricted=gds.*
dbms.security.procedures.allowlist=gds.*
```

### Verify Installation

```cypher
// Check GDS version
RETURN gds.version()

// List available algorithms
CALL gds.list()
```

---

## 25.2 Graph Projections

### What are Projections?

Projections are in-memory graphs optimized for algorithms. They're separate from your stored graph.

### Native Projection

```cypher
// Project a graph into memory
CALL gds.graph.project(
    'myGraph',                    // Graph name
    'Person',                     // Node label(s)
    'KNOWS'                       // Relationship type(s)
)
YIELD graphName, nodeCount, relationshipCount
RETURN graphName, nodeCount, relationshipCount

// Multiple labels and relationship types
CALL gds.graph.project(
    'socialGraph',
    ['Person', 'Company'],
    ['KNOWS', 'WORKS_FOR']
)

// With relationship properties
CALL gds.graph.project(
    'weightedGraph',
    'Person',
    {
        KNOWS: {
            type: 'KNOWS',
            properties: ['strength', 'since']
        }
    }
)

// With node properties
CALL gds.graph.project(
    'personGraph',
    {
        Person: {
            properties: ['age', 'score']
        }
    },
    'KNOWS'
)
```

### Cypher Projection

For complex filtering:

```cypher
CALL gds.graph.project.cypher(
    'customGraph',
    'MATCH (n:Person) WHERE n.active = true RETURN id(n) AS id, labels(n) AS labels, n.age AS age',
    'MATCH (a:Person)-[r:KNOWS]->(b:Person) WHERE r.strength > 0.5 RETURN id(a) AS source, id(b) AS target, r.strength AS weight'
)
```

### Managing Projections

```cypher
// List all projections
CALL gds.graph.list()
YIELD graphName, nodeCount, relationshipCount, memoryUsage
RETURN *

// Check if graph exists
CALL gds.graph.exists('myGraph')
YIELD exists
RETURN exists

// Drop projection
CALL gds.graph.drop('myGraph')

// Drop if exists
CALL gds.graph.drop('myGraph', false)  // false = don't fail if not exists
```

---

## 25.3 Algorithm Execution Modes

### Execution Modes

| Mode | Purpose | Returns |
|------|---------|---------|
| `stream` | Return results as stream | Results only |
| `stats` | Return aggregate statistics | Statistics |
| `mutate` | Write to in-memory graph | Statistics |
| `write` | Write to Neo4j database | Statistics |

### Example: PageRank in Different Modes

```cypher
// Stream: Get results without storing
CALL gds.pageRank.stream('myGraph')
YIELD nodeId, score
RETURN gds.util.asNode(nodeId).name AS name, score
ORDER BY score DESC
LIMIT 10

// Stats: Get statistics only
CALL gds.pageRank.stats('myGraph')
YIELD ranIterations, didConverge, preProcessingMillis, computeMillis
RETURN *

// Mutate: Store in projection (fast, temporary)
CALL gds.pageRank.mutate('myGraph', {mutateProperty: 'pageRank'})
YIELD nodePropertiesWritten, ranIterations
RETURN *

// Write: Store in Neo4j (persistent)
CALL gds.pageRank.write('myGraph', {writeProperty: 'pageRank'})
YIELD nodePropertiesWritten, ranIterations
RETURN *
```

---

## 25.4 Centrality Algorithms

### PageRank

Measures node importance based on incoming relationships:

```cypher
// Create projection
CALL gds.graph.project('web', 'Page', 'LINKS_TO')

// Run PageRank
CALL gds.pageRank.stream('web', {
    maxIterations: 20,
    dampingFactor: 0.85
})
YIELD nodeId, score
RETURN gds.util.asNode(nodeId).url AS page, score
ORDER BY score DESC
LIMIT 10

// Personalized PageRank (from specific source)
MATCH (source:Page {url: 'homepage'})
CALL gds.pageRank.stream('web', {
    sourceNodes: [source],
    maxIterations: 20
})
YIELD nodeId, score
RETURN gds.util.asNode(nodeId).url AS page, score
ORDER BY score DESC
```

### Betweenness Centrality

Nodes that act as bridges:

```cypher
CALL gds.betweenness.stream('socialGraph')
YIELD nodeId, score
RETURN gds.util.asNode(nodeId).name AS name, score
ORDER BY score DESC
LIMIT 10
```

### Degree Centrality

Count of connections:

```cypher
CALL gds.degree.stream('socialGraph', {
    orientation: 'UNDIRECTED'
})
YIELD nodeId, score
RETURN gds.util.asNode(nodeId).name AS name, score AS connections
ORDER BY score DESC
```

### Closeness Centrality

How quickly a node can reach others:

```cypher
CALL gds.closeness.stream('socialGraph')
YIELD nodeId, score
RETURN gds.util.asNode(nodeId).name AS name, score
ORDER BY score DESC
```

---

## 25.5 Community Detection

### Louvain (Modularity Optimization)

Best for finding communities:

```cypher
// Detect communities
CALL gds.louvain.stream('socialGraph')
YIELD nodeId, communityId
RETURN communityId, collect(gds.util.asNode(nodeId).name) AS members
ORDER BY size(members) DESC

// With intermediate communities
CALL gds.louvain.stream('socialGraph', {
    includeIntermediateCommunities: true
})
YIELD nodeId, communityId, intermediateCommunityIds
RETURN gds.util.asNode(nodeId).name AS name, communityId, intermediateCommunityIds
```

### Label Propagation

Fast community detection:

```cypher
CALL gds.labelPropagation.stream('socialGraph', {
    maxIterations: 10
})
YIELD nodeId, communityId
RETURN communityId, count(*) AS size, 
       collect(gds.util.asNode(nodeId).name) AS members
ORDER BY size DESC
```

### Weakly Connected Components

Find disconnected groups:

```cypher
CALL gds.wcc.stream('socialGraph')
YIELD nodeId, componentId
RETURN componentId, count(*) AS size
ORDER BY size DESC
```

### Strongly Connected Components

For directed graphs:

```cypher
CALL gds.scc.stream('directedGraph')
YIELD nodeId, componentId
RETURN componentId, count(*) AS size
ORDER BY size DESC
```

### Triangle Count

Find clustering:

```cypher
CALL gds.triangleCount.stream('socialGraph')
YIELD nodeId, triangleCount
RETURN gds.util.asNode(nodeId).name AS name, triangleCount
ORDER BY triangleCount DESC
```

---

## 25.6 Similarity Algorithms

### Node Similarity

Find similar nodes based on shared neighbors:

```cypher
CALL gds.nodeSimilarity.stream('purchaseGraph', {
    topK: 10,
    similarityCutoff: 0.5
})
YIELD node1, node2, similarity
RETURN gds.util.asNode(node1).name AS person1,
       gds.util.asNode(node2).name AS person2,
       similarity
ORDER BY similarity DESC
```

### K-Nearest Neighbors (KNN)

Based on node properties:

```cypher
// Project with properties
CALL gds.graph.project(
    'productGraph',
    {
        Product: {
            properties: ['price', 'rating', 'categoryVector']
        }
    },
    '*'
)

// Find similar products
CALL gds.knn.stream('productGraph', {
    topK: 5,
    nodeProperties: ['price', 'rating'],
    sampleRate: 0.5,
    randomSeed: 42
})
YIELD node1, node2, similarity
RETURN gds.util.asNode(node1).name AS product1,
       gds.util.asNode(node2).name AS product2,
       similarity
```

### Jaccard Similarity

```cypher
// Manual Jaccard calculation
MATCH (p1:Person)-[:PURCHASED]->(product)<-[:PURCHASED]-(p2:Person)
WHERE p1 <> p2
WITH p1, p2, count(product) AS intersection
MATCH (p1)-[:PURCHASED]->(p1Products)
WITH p1, p2, intersection, count(DISTINCT p1Products) AS p1Count
MATCH (p2)-[:PURCHASED]->(p2Products)
WITH p1, p2, intersection, p1Count, count(DISTINCT p2Products) AS p2Count
RETURN p1.name, p2.name, 
       toFloat(intersection) / (p1Count + p2Count - intersection) AS jaccard
ORDER BY jaccard DESC
```

---

## 25.7 Path Finding

### Shortest Path

```cypher
// Dijkstra's algorithm
MATCH (source:City {name: 'New York'}), (target:City {name: 'Los Angeles'})
CALL gds.shortestPath.dijkstra.stream('roadNetwork', {
    sourceNode: source,
    targetNode: target,
    relationshipWeightProperty: 'distance'
})
YIELD index, sourceNode, targetNode, totalCost, nodeIds, costs, path
RETURN totalCost AS distance,
       [nodeId IN nodeIds | gds.util.asNode(nodeId).name] AS route

// A* algorithm (with heuristic)
CALL gds.shortestPath.astar.stream('roadNetwork', {
    sourceNode: source,
    targetNode: target,
    latitudeProperty: 'latitude',
    longitudeProperty: 'longitude',
    relationshipWeightProperty: 'distance'
})
YIELD totalCost, nodeIds
RETURN totalCost, [nodeId IN nodeIds | gds.util.asNode(nodeId).name] AS route
```

### All Shortest Paths

```cypher
MATCH (source:Person {name: 'Alice'})
CALL gds.allShortestPaths.dijkstra.stream('socialGraph', {
    sourceNode: source,
    relationshipWeightProperty: 'weight'
})
YIELD index, sourceNode, targetNode, totalCost, nodeIds
RETURN gds.util.asNode(targetNode).name AS destination, totalCost
ORDER BY totalCost
```

### Breadth First Search

```cypher
MATCH (source:Person {name: 'Alice'})
CALL gds.bfs.stream('socialGraph', {
    sourceNode: source,
    maxDepth: 3
})
YIELD path
RETURN path
```

---

## 25.8 Node Embeddings

### FastRP (Fast Random Projection)

Generate node vectors:

```cypher
// Create embeddings
CALL gds.fastRP.stream('socialGraph', {
    embeddingDimension: 128,
    iterationWeights: [0.0, 1.0, 1.0]
})
YIELD nodeId, embedding
RETURN gds.util.asNode(nodeId).name AS name, embedding

// Write embeddings to database
CALL gds.fastRP.write('socialGraph', {
    embeddingDimension: 128,
    writeProperty: 'embedding'
})
YIELD nodePropertiesWritten
```

### Node2Vec

```cypher
CALL gds.node2vec.stream('socialGraph', {
    embeddingDimension: 64,
    walkLength: 80,
    walksPerNode: 10,
    returnFactor: 1.0,
    inOutFactor: 1.0
})
YIELD nodeId, embedding
RETURN gds.util.asNode(nodeId).name AS name, embedding
```

### Using Embeddings for Similarity

```cypher
// After creating embeddings
CALL gds.knn.stream('socialGraph', {
    topK: 5,
    nodeProperties: ['embedding']
})
YIELD node1, node2, similarity
RETURN gds.util.asNode(node1).name AS person1,
       gds.util.asNode(node2).name AS person2,
       similarity
ORDER BY similarity DESC
```

---

## 25.9 Link Prediction

### Common Neighbors

```cypher
CALL gds.linkPrediction.commonNeighbors.stream({
    sourceNode: person1,
    targetNode: person2
})
```

### Preferential Attachment

```cypher
// Score potential links
MATCH (p1:Person), (p2:Person)
WHERE p1 <> p2 AND NOT (p1)-[:KNOWS]-(p2)
WITH p1, p2
CALL gds.alpha.linkprediction.preferentialAttachment.stream({
    node1: p1,
    node2: p2
})
YIELD score
RETURN p1.name, p2.name, score
ORDER BY score DESC
LIMIT 10
```

### Using ML for Link Prediction

```cypher
// Create training data
CALL gds.graph.project(
    'linkPredictionGraph',
    'Person',
    {
        KNOWS: {orientation: 'UNDIRECTED'}
    }
)

// Split into train/test
CALL gds.beta.graph.relationships.split.mutate('linkPredictionGraph', {
    relationshipType: 'KNOWS',
    holdoutFraction: 0.2,
    negativeSamplingRatio: 1.0,
    randomSeed: 42
})

// Train link prediction model
CALL gds.beta.pipeline.linkPrediction.create('lpPipeline')
// Add features and model configuration...
```

---

## 25.10 Python Integration

```python
from neo4j import GraphDatabase
from typing import List, Dict
import numpy as np

URI = "neo4j://localhost:7687"
AUTH = ("neo4j", "password")

class GraphDataScience:
    def __init__(self, uri, auth):
        self.driver = GraphDatabase.driver(uri, auth=auth)
    
    def close(self):
        self.driver.close()
    
    def project_graph(self, graph_name: str, node_label: str, 
                      rel_type: str, node_properties: List[str] = None):
        """Create a graph projection."""
        with self.driver.session() as session:
            # Drop if exists
            session.run("CALL gds.graph.drop($name, false)", name=graph_name)
            
            if node_properties:
                result = session.run("""
                    CALL gds.graph.project(
                        $name,
                        {node: {label: $label, properties: $props}},
                        $relType
                    )
                    YIELD graphName, nodeCount, relationshipCount
                    RETURN graphName, nodeCount, relationshipCount
                """, name=graph_name, label=node_label, 
                    props=node_properties, relType=rel_type)
            else:
                result = session.run("""
                    CALL gds.graph.project($name, $label, $relType)
                    YIELD graphName, nodeCount, relationshipCount
                    RETURN graphName, nodeCount, relationshipCount
                """, name=graph_name, label=node_label, relType=rel_type)
            
            return dict(result.single())
    
    def run_pagerank(self, graph_name: str, write: bool = False) -> List[Dict]:
        """Run PageRank algorithm."""
        with self.driver.session() as session:
            if write:
                result = session.run("""
                    CALL gds.pageRank.write($graph, {writeProperty: 'pageRank'})
                    YIELD nodePropertiesWritten, ranIterations, didConverge
                    RETURN nodePropertiesWritten, ranIterations, didConverge
                """, graph=graph_name)
                return dict(result.single())
            else:
                result = session.run("""
                    CALL gds.pageRank.stream($graph)
                    YIELD nodeId, score
                    RETURN gds.util.asNode(nodeId).name AS name, score
                    ORDER BY score DESC
                    LIMIT 100
                """, graph=graph_name)
                return [dict(r) for r in result]
    
    def run_louvain(self, graph_name: str) -> List[Dict]:
        """Run Louvain community detection."""
        with self.driver.session() as session:
            result = session.run("""
                CALL gds.louvain.stream($graph)
                YIELD nodeId, communityId
                RETURN communityId, 
                       collect(gds.util.asNode(nodeId).name) AS members,
                       count(*) AS size
                ORDER BY size DESC
            """, graph=graph_name)
            return [dict(r) for r in result]
    
    def compute_embeddings(self, graph_name: str, 
                           dimension: int = 128) -> Dict[str, np.ndarray]:
        """Compute FastRP embeddings."""
        with self.driver.session() as session:
            result = session.run("""
                CALL gds.fastRP.stream($graph, {
                    embeddingDimension: $dim
                })
                YIELD nodeId, embedding
                RETURN gds.util.asNode(nodeId).name AS name, embedding
            """, graph=graph_name, dim=dimension)
            
            return {r['name']: np.array(r['embedding']) for r in result}
    
    def find_similar_nodes(self, graph_name: str, 
                           top_k: int = 10) -> List[Dict]:
        """Find similar nodes using Node Similarity."""
        with self.driver.session() as session:
            result = session.run("""
                CALL gds.nodeSimilarity.stream($graph, {
                    topK: $k,
                    similarityCutoff: 0.1
                })
                YIELD node1, node2, similarity
                RETURN gds.util.asNode(node1).name AS entity1,
                       gds.util.asNode(node2).name AS entity2,
                       similarity
                ORDER BY similarity DESC
            """, graph=graph_name, k=top_k)
            return [dict(r) for r in result]
    
    def shortest_path(self, graph_name: str, source_name: str, 
                      target_name: str, weight_property: str = None):
        """Find shortest path between two nodes."""
        with self.driver.session() as session:
            if weight_property:
                result = session.run("""
                    MATCH (source {name: $source}), (target {name: $target})
                    CALL gds.shortestPath.dijkstra.stream($graph, {
                        sourceNode: source,
                        targetNode: target,
                        relationshipWeightProperty: $weight
                    })
                    YIELD totalCost, nodeIds, path
                    RETURN totalCost,
                           [nodeId IN nodeIds | gds.util.asNode(nodeId).name] AS route
                """, graph=graph_name, source=source_name, 
                    target=target_name, weight=weight_property)
            else:
                result = session.run("""
                    MATCH (source {name: $source}), (target {name: $target})
                    CALL gds.shortestPath.dijkstra.stream($graph, {
                        sourceNode: source,
                        targetNode: target
                    })
                    YIELD totalCost, nodeIds
                    RETURN totalCost,
                           [nodeId IN nodeIds | gds.util.asNode(nodeId).name] AS route
                """, graph=graph_name, source=source_name, target=target_name)
            
            record = result.single()
            return {'cost': record['totalCost'], 'route': record['route']} if record else None

# Usage
gds = GraphDataScience(URI, AUTH)
try:
    # Project graph
    stats = gds.project_graph('social', 'Person', 'KNOWS')
    print(f"Projected {stats['nodeCount']} nodes")
    
    # Run PageRank
    pagerank = gds.run_pagerank('social')
    print("Top 5 by PageRank:")
    for p in pagerank[:5]:
        print(f"  {p['name']}: {p['score']:.4f}")
    
    # Find communities
    communities = gds.run_louvain('social')
    print(f"\nFound {len(communities)} communities")
    
    # Compute embeddings
    embeddings = gds.compute_embeddings('social', dimension=64)
    print(f"\nComputed embeddings for {len(embeddings)} nodes")
    
finally:
    gds.close()
```

---

## Summary

### Key Algorithms

| Category | Algorithm | Use Case |
|----------|-----------|----------|
| **Centrality** | PageRank | Node importance |
| **Centrality** | Betweenness | Bridge nodes |
| **Community** | Louvain | Community detection |
| **Community** | Label Propagation | Fast clustering |
| **Similarity** | Node Similarity | Similar nodes |
| **Similarity** | KNN | Property-based similarity |
| **Path** | Dijkstra | Shortest weighted path |
| **Embedding** | FastRP | Node vectors |

### Workflow

1. **Project** graph into memory
2. **Run** algorithm (stream/stats/mutate/write)
3. **Analyze** or **persist** results
4. **Drop** projection when done

---

## Exercises

### Exercise 25.1: Centrality Analysis
1. Project a social network graph
2. Run PageRank, Betweenness, and Degree centrality
3. Compare results - who are the key influencers?

### Exercise 25.2: Community Detection
1. Run Louvain on a graph
2. Visualize communities
3. Analyze community characteristics

### Exercise 25.3: Recommendation System
1. Create embeddings for users
2. Find similar users using KNN
3. Recommend items based on similar users' preferences

---

**Next Chapter: [Chapter 26: Centrality Algorithms](26-centrality-algorithms.md)**
