# Chapter 28: Similarity Algorithms

## Learning Objectives
By the end of this chapter, you will:
- Understand different similarity measures
- Apply Node Similarity and KNN algorithms
- Build similarity graphs for recommendations
- Use embeddings for similarity computation
- Implement collaborative filtering

---

## 28.1 Understanding Similarity

### Types of Similarity

| Type | Based On | Example |
|------|----------|---------|
| **Structural** | Graph connections | Users who follow similar people |
| **Attribute** | Node properties | Products with similar prices |
| **Behavioral** | Interaction patterns | Users who buy similar items |
| **Embedding** | Vector representations | Similar feature vectors |

### Common Similarity Metrics

| Metric | Formula | Range |
|--------|---------|-------|
| Jaccard | \|A∩B\| / \|A∪B\| | [0, 1] |
| Overlap | \|A∩B\| / min(\|A\|, \|B\|) | [0, 1] |
| Cosine | A·B / (\|A\|×\|B\|) | [-1, 1] |
| Euclidean | √Σ(ai - bi)² | [0, ∞] |
| Pearson | cov(A,B) / (σA×σB) | [-1, 1] |

---

## 28.2 Node Similarity

### How It Works

Compares nodes based on their neighborhood overlap:

```
similarity(A, B) = |neighbors(A) ∩ neighbors(B)| / |neighbors(A) ∪ neighbors(B)|
```

### Implementation

```cypher
// Create projection
CALL gds.graph.project(
    'purchaseGraph',
    ['Person', 'Product'],
    {PURCHASED: {type: 'PURCHASED'}}
)

// Find similar customers (based on products purchased)
CALL gds.nodeSimilarity.stream('purchaseGraph', {
    topK: 10,
    similarityCutoff: 0.1
})
YIELD node1, node2, similarity
RETURN gds.util.asNode(node1).name AS person1,
       gds.util.asNode(node2).name AS person2,
       similarity
ORDER BY similarity DESC

// Only compare Person nodes
CALL gds.nodeSimilarity.stream('purchaseGraph', {
    topK: 5,
    similarityCutoff: 0.1,
    sourceNodeFilter: 'Person',
    targetNodeFilter: 'Person'
})
YIELD node1, node2, similarity
RETURN gds.util.asNode(node1).name AS person1,
       gds.util.asNode(node2).name AS person2,
       similarity
ORDER BY similarity DESC
```

### Configuration Options

```cypher
// Top K per node
CALL gds.nodeSimilarity.stream('purchaseGraph', {
    topK: 5,                    // Top 5 similar nodes per node
    topN: 100,                  // Total top 100 pairs
    bottomK: 5,                 // Bottom 5 (least similar)
    similarityCutoff: 0.0,      // Minimum similarity
    degreeCutoff: 1            // Minimum connections to include
})
YIELD node1, node2, similarity
RETURN *

// Weighted similarity
CALL gds.graph.project(
    'ratedProducts',
    ['Person', 'Product'],
    {RATED: {type: 'RATED', properties: 'rating'}}
)

CALL gds.nodeSimilarity.stream('ratedProducts', {
    relationshipWeightProperty: 'rating'
})
YIELD node1, node2, similarity
RETURN gds.util.asNode(node1).name, 
       gds.util.asNode(node2).name, 
       similarity
ORDER BY similarity DESC
```

### Write Similarity Relationships

```cypher
// Create SIMILAR relationships
CALL gds.nodeSimilarity.write('purchaseGraph', {
    writeRelationshipType: 'SIMILAR_TO',
    writeProperty: 'score',
    topK: 10,
    similarityCutoff: 0.3
})
YIELD nodesCompared, relationshipsWritten
RETURN nodesCompared, relationshipsWritten

// Query the created relationships
MATCH (p1:Person)-[s:SIMILAR_TO]->(p2:Person)
RETURN p1.name, p2.name, s.score
ORDER BY s.score DESC
```

---

## 28.3 K-Nearest Neighbors (KNN)

### How It Works

Finds similar nodes based on node property vectors rather than graph structure.

### Implementation

```cypher
// Project with node properties
CALL gds.graph.project(
    'productProperties',
    {
        Product: {
            properties: ['price', 'rating', 'categoryId']
        }
    },
    '*'
)

// Find similar products by properties
CALL gds.knn.stream('productProperties', {
    topK: 10,
    nodeProperties: ['price', 'rating', 'categoryId'],
    sampleRate: 0.5,
    deltaThreshold: 0.001,
    randomSeed: 42
})
YIELD node1, node2, similarity
RETURN gds.util.asNode(node1).name AS product1,
       gds.util.asNode(node2).name AS product2,
       similarity
ORDER BY similarity DESC
```

### Configuration

```cypher
// Multiple node properties with weights
CALL gds.knn.stream('productProperties', {
    topK: 5,
    nodeProperties: {
        price: 'EUCLIDEAN',
        rating: 'COSINE',
        categoryVector: 'COSINE'
    },
    sampleRate: 1.0,            // Sample all nodes
    maxIterations: 100,
    deltaThreshold: 0.001,      // Stop when similarity changes < threshold
    randomJoins: 10,            // Random neighbors to consider
    initialSampler: 'uniform'   // or 'randomWalk'
})
YIELD node1, node2, similarity
RETURN *

// Write results
CALL gds.knn.write('productProperties', {
    topK: 5,
    nodeProperties: ['price', 'rating'],
    writeRelationshipType: 'KNN_SIMILAR',
    writeProperty: 'knnScore'
})
YIELD relationshipsWritten, nodePairsConsidered
RETURN *
```

### KNN with Embeddings

```cypher
// First create embeddings
CALL gds.fastRP.mutate('socialGraph', {
    embeddingDimension: 128,
    mutateProperty: 'embedding'
})

// Then use KNN on embeddings
CALL gds.knn.stream('socialGraph', {
    topK: 10,
    nodeProperties: ['embedding']
})
YIELD node1, node2, similarity
RETURN gds.util.asNode(node1).name AS person1,
       gds.util.asNode(node2).name AS person2,
       similarity
ORDER BY similarity DESC
```

---

## 28.4 Manual Similarity Calculations

### Jaccard Similarity

```cypher
// Calculate Jaccard similarity between users
MATCH (p1:Person {name: 'Alice'})-[:PURCHASED]->(product)<-[:PURCHASED]-(p2:Person)
WHERE p1 <> p2
WITH p1, p2, count(product) AS intersection
MATCH (p1)-[:PURCHASED]->(p1Products)
WITH p1, p2, intersection, count(DISTINCT p1Products) AS p1Count
MATCH (p2)-[:PURCHASED]->(p2Products)
WITH p1, p2, intersection, p1Count, count(DISTINCT p2Products) AS p2Count
RETURN p2.name AS person,
       intersection,
       p1Count,
       p2Count,
       toFloat(intersection) / (p1Count + p2Count - intersection) AS jaccard
ORDER BY jaccard DESC

// Using APOC
MATCH (p1:Person {name: 'Alice'})-[:PURCHASED]->(product1)
WITH p1, collect(id(product1)) AS products1
MATCH (p2:Person)-[:PURCHASED]->(product2)
WHERE p1 <> p2
WITH p1, products1, p2, collect(id(product2)) AS products2
RETURN p2.name AS person,
       gds.similarity.jaccard(products1, products2) AS jaccard
ORDER BY jaccard DESC
```

### Cosine Similarity

```cypher
// Cosine similarity for rating vectors
MATCH (p1:Person {name: 'Alice'})-[r1:RATED]->(product)<-[r2:RATED]-(p2:Person)
WHERE p1 <> p2
WITH p1, p2, 
     collect(r1.rating) AS ratings1,
     collect(r2.rating) AS ratings2
RETURN p2.name,
       gds.similarity.cosine(ratings1, ratings2) AS cosine
ORDER BY cosine DESC

// Manual cosine calculation
MATCH (p1:Person {name: 'Alice'})-[r1:RATED]->(product)<-[r2:RATED]-(p2:Person)
WHERE p1 <> p2
WITH p1, p2,
     sum(r1.rating * r2.rating) AS dotProduct,
     sqrt(sum(r1.rating * r1.rating)) AS norm1,
     sqrt(sum(r2.rating * r2.rating)) AS norm2
RETURN p2.name,
       dotProduct / (norm1 * norm2) AS cosine
ORDER BY cosine DESC
```

### Overlap Coefficient

```cypher
// Overlap coefficient
MATCH (p1:Person {name: 'Alice'})-[:PURCHASED]->(product)<-[:PURCHASED]-(p2:Person)
WHERE p1 <> p2
WITH p1, p2, count(product) AS intersection
MATCH (p1)-[:PURCHASED]->(p1Products)
WITH p1, p2, intersection, count(DISTINCT p1Products) AS p1Count
MATCH (p2)-[:PURCHASED]->(p2Products)
WITH p1, p2, intersection, p1Count, count(DISTINCT p2Products) AS p2Count
RETURN p2.name,
       toFloat(intersection) / 
       CASE WHEN p1Count < p2Count THEN p1Count ELSE p2Count END AS overlap
ORDER BY overlap DESC
```

---

## 28.5 Building Recommendation Systems

### Collaborative Filtering

```cypher
// User-based collaborative filtering
// Step 1: Find similar users
MATCH (target:Person {name: 'Alice'})-[:PURCHASED]->(product)<-[:PURCHASED]-(similar:Person)
WHERE target <> similar
WITH target, similar, count(product) AS commonProducts
ORDER BY commonProducts DESC
LIMIT 10

// Step 2: Find products similar users bought that target hasn't
MATCH (similar)-[:PURCHASED]->(rec:Product)
WHERE NOT (target)-[:PURCHASED]->(rec)
RETURN rec.name, count(*) AS score, collect(similar.name) AS recommenders
ORDER BY score DESC
LIMIT 10
```

### Item-based Recommendations

```cypher
// Find similar products to what user purchased
MATCH (target:Person {name: 'Alice'})-[:PURCHASED]->(owned:Product)
MATCH (owned)<-[:PURCHASED]-(other:Person)-[:PURCHASED]->(rec:Product)
WHERE target <> other AND NOT (target)-[:PURCHASED]->(rec)
WITH rec, count(*) AS cooccurrences, collect(DISTINCT owned.name) AS basedOn
RETURN rec.name, cooccurrences, basedOn
ORDER BY cooccurrences DESC
LIMIT 10
```

### Hybrid Approach

```cypher
// Combine user similarity with item features
MATCH (target:Person {name: 'Alice'})

// Find similar users
CALL {
    WITH target
    MATCH (target)-[:PURCHASED]->(p)<-[:PURCHASED]-(similar:Person)
    WHERE target <> similar
    WITH similar, count(p) AS overlap
    ORDER BY overlap DESC
    LIMIT 20
    RETURN similar
}

// Get recommendations from similar users
MATCH (similar)-[r:RATED]->(product:Product)
WHERE NOT (target)-[:PURCHASED]->(product)
  AND r.rating >= 4

// Weight by user similarity and item attributes
WITH product, 
     avg(r.rating) AS avgRating,
     count(similar) AS recommenderCount,
     product.popularity AS popularity
RETURN product.name,
       avgRating,
       recommenderCount,
       (avgRating * 0.4) + (recommenderCount * 0.3) + (popularity * 0.3) AS score
ORDER BY score DESC
LIMIT 10
```

---

## 28.6 Similarity Graphs

### Creating a Similarity Network

```cypher
// Project bipartite graph
CALL gds.graph.project(
    'userProductGraph',
    ['Person', 'Product'],
    'PURCHASED'
)

// Create similarity relationships
CALL gds.nodeSimilarity.write('userProductGraph', {
    writeRelationshipType: 'SIMILAR_TASTE',
    writeProperty: 'similarity',
    topK: 5,
    similarityCutoff: 0.3,
    sourceNodeFilter: 'Person',
    targetNodeFilter: 'Person'
})

// Query the similarity network
MATCH path = (p1:Person)-[s:SIMILAR_TASTE]->(p2:Person)
WHERE s.similarity > 0.5
RETURN path
```

### Analyzing Similarity Clusters

```cypher
// Project the similarity graph
CALL gds.graph.project(
    'similarityGraph',
    'Person',
    {SIMILAR_TASTE: {properties: 'similarity'}}
)

// Find communities in the similarity network
CALL gds.louvain.stream('similarityGraph', {
    relationshipWeightProperty: 'similarity'
})
YIELD nodeId, communityId
RETURN communityId,
       count(*) AS size,
       collect(gds.util.asNode(nodeId).name) AS members
ORDER BY size DESC
```

---

## 28.7 Filtered Similarity

### Similarity Within Categories

```cypher
// Only compare products within same category
MATCH (p:Product)
WITH p.category AS category, collect(p) AS products
UNWIND products AS p1
UNWIND products AS p2
WHERE id(p1) < id(p2)
MATCH (p1)<-[:PURCHASED]-(buyer)-[:PURCHASED]->(p2)
WITH p1, p2, category, count(buyer) AS coBuyers
MATCH (p1)<-[:PURCHASED]-(buyer1)
WITH p1, p2, category, coBuyers, count(buyer1) AS p1Buyers
MATCH (p2)<-[:PURCHASED]-(buyer2)
WITH p1, p2, category, coBuyers, p1Buyers, count(buyer2) AS p2Buyers
RETURN category,
       p1.name AS product1,
       p2.name AS product2,
       toFloat(coBuyers) / (p1Buyers + p2Buyers - coBuyers) AS jaccard
ORDER BY category, jaccard DESC
```

### Time-Weighted Similarity

```cypher
// Weight recent interactions more heavily
MATCH (p1:Person {name: 'Alice'})-[r1:PURCHASED]->(product)<-[r2:PURCHASED]-(p2:Person)
WHERE p1 <> p2
WITH p1, p2, product,
     // Decay factor based on recency
     exp(-0.01 * duration.between(r1.date, date()).days) AS weight1,
     exp(-0.01 * duration.between(r2.date, date()).days) AS weight2
WITH p1, p2, sum(weight1 * weight2) AS weightedIntersection
RETURN p2.name, weightedIntersection
ORDER BY weightedIntersection DESC
```

---

## 28.8 Python Integration

```python
from neo4j import GraphDatabase
from typing import List, Dict, Tuple
import numpy as np
from collections import defaultdict

URI = "neo4j://localhost:7687"
AUTH = ("neo4j", "password")

class SimilarityEngine:
    def __init__(self, uri, auth):
        self.driver = GraphDatabase.driver(uri, auth=auth)
    
    def close(self):
        self.driver.close()
    
    def project_bipartite_graph(self, name: str, 
                                 node_labels: List[str],
                                 rel_type: str) -> Dict:
        """Project a bipartite graph for similarity."""
        with self.driver.session() as session:
            session.run("CALL gds.graph.drop($name, false)", name=name)
            result = session.run("""
                CALL gds.graph.project($name, $labels, $relType)
                YIELD nodeCount, relationshipCount
                RETURN nodeCount, relationshipCount
            """, name=name, labels=node_labels, relType=rel_type)
            return dict(result.single())
    
    def find_similar_nodes(self, graph_name: str,
                           top_k: int = 10,
                           cutoff: float = 0.1,
                           source_filter: str = None,
                           target_filter: str = None) -> List[Dict]:
        """Find similar nodes using Node Similarity algorithm."""
        with self.driver.session() as session:
            config = {
                'topK': top_k,
                'similarityCutoff': cutoff
            }
            if source_filter:
                config['sourceNodeFilter'] = source_filter
            if target_filter:
                config['targetNodeFilter'] = target_filter
            
            result = session.run("""
                CALL gds.nodeSimilarity.stream($graph, $config)
                YIELD node1, node2, similarity
                RETURN gds.util.asNode(node1).name AS entity1,
                       gds.util.asNode(node2).name AS entity2,
                       similarity
                ORDER BY similarity DESC
            """, graph=graph_name, config=config)
            
            return [dict(r) for r in result]
    
    def find_knn(self, graph_name: str,
                 properties: List[str],
                 top_k: int = 10) -> List[Dict]:
        """Find similar nodes using KNN on properties."""
        with self.driver.session() as session:
            result = session.run("""
                CALL gds.knn.stream($graph, {
                    topK: $k,
                    nodeProperties: $props,
                    sampleRate: 1.0
                })
                YIELD node1, node2, similarity
                RETURN gds.util.asNode(node1).name AS entity1,
                       gds.util.asNode(node2).name AS entity2,
                       similarity
                ORDER BY similarity DESC
            """, graph=graph_name, k=top_k, props=properties)
            
            return [dict(r) for r in result]
    
    def create_similarity_relationships(self, graph_name: str,
                                        rel_type: str,
                                        top_k: int = 5,
                                        cutoff: float = 0.3) -> Dict:
        """Write similarity relationships to database."""
        with self.driver.session() as session:
            result = session.run("""
                CALL gds.nodeSimilarity.write($graph, {
                    writeRelationshipType: $relType,
                    writeProperty: 'similarity',
                    topK: $k,
                    similarityCutoff: $cutoff
                })
                YIELD nodesCompared, relationshipsWritten
                RETURN nodesCompared, relationshipsWritten
            """, graph=graph_name, relType=rel_type, k=top_k, cutoff=cutoff)
            
            return dict(result.single())
    
    def recommend_items(self, user_name: str, 
                        top_n: int = 10) -> List[Dict]:
        """Recommend items using collaborative filtering."""
        with self.driver.session() as session:
            result = session.run("""
                // Find similar users
                MATCH (target:Person {name: $user})-[:PURCHASED]->(p)<-[:PURCHASED]-(similar:Person)
                WHERE target <> similar
                WITH target, similar, count(p) AS overlap
                ORDER BY overlap DESC
                LIMIT 20
                
                // Get products from similar users
                MATCH (similar)-[:PURCHASED]->(rec:Product)
                WHERE NOT (target)-[:PURCHASED]->(rec)
                WITH rec, count(DISTINCT similar) AS recommenders, 
                     sum(overlap) AS totalOverlap
                
                RETURN rec.name AS product,
                       recommenders,
                       totalOverlap,
                       recommenders * 1.0 + totalOverlap * 0.1 AS score
                ORDER BY score DESC
                LIMIT $limit
            """, user=user_name, limit=top_n)
            
            return [dict(r) for r in result]
    
    def find_similar_to(self, entity_name: str,
                        entity_label: str,
                        rel_type: str,
                        top_n: int = 10) -> List[Dict]:
        """Find entities similar to a specific one."""
        with self.driver.session() as session:
            result = session.run(f"""
                MATCH (target:{entity_label} {{name: $name}})-[:{rel_type}]->(common)<-[:{rel_type}]-(similar:{entity_label})
                WHERE target <> similar
                WITH target, similar, count(common) AS intersection
                MATCH (target)-[:{rel_type}]->(t1)
                WITH target, similar, intersection, count(DISTINCT t1) AS targetCount
                MATCH (similar)-[:{rel_type}]->(s1)
                WITH similar, intersection, targetCount, count(DISTINCT s1) AS similarCount
                RETURN similar.name AS name,
                       intersection,
                       targetCount,
                       similarCount,
                       toFloat(intersection) / (targetCount + similarCount - intersection) AS jaccard
                ORDER BY jaccard DESC
                LIMIT $limit
            """, name=entity_name, limit=top_n)
            
            return [dict(r) for r in result]
    
    def compute_all_pairs_similarity(self, label: str,
                                      rel_type: str) -> Dict[Tuple[str, str], float]:
        """Compute Jaccard similarity for all pairs."""
        with self.driver.session() as session:
            result = session.run(f"""
                MATCH (n1:{label})-[:{rel_type}]->(common)<-[:{rel_type}]-(n2:{label})
                WHERE id(n1) < id(n2)
                WITH n1, n2, count(common) AS intersection
                MATCH (n1)-[:{rel_type}]->(a1)
                WITH n1, n2, intersection, count(DISTINCT a1) AS n1Count
                MATCH (n2)-[:{rel_type}]->(a2)
                RETURN n1.name AS entity1, 
                       n2.name AS entity2,
                       toFloat(intersection) / (n1Count + count(DISTINCT a2) - intersection) AS jaccard
            """)
            
            return {(r['entity1'], r['entity2']): r['jaccard'] for r in result}

# Usage
engine = SimilarityEngine(URI, AUTH)
try:
    # Project bipartite graph
    stats = engine.project_bipartite_graph(
        'customerProducts',
        ['Person', 'Product'],
        'PURCHASED'
    )
    print(f"Projected: {stats}")
    
    # Find similar customers
    similar_customers = engine.find_similar_nodes(
        'customerProducts',
        top_k=10,
        cutoff=0.2,
        source_filter='Person',
        target_filter='Person'
    )
    print("\nSimilar Customers:")
    for s in similar_customers[:5]:
        print(f"  {s['entity1']} <-> {s['entity2']}: {s['similarity']:.3f}")
    
    # Get recommendations
    recommendations = engine.recommend_items('Alice', top_n=5)
    print("\nRecommendations for Alice:")
    for r in recommendations:
        print(f"  {r['product']}: score={r['score']:.2f} ({r['recommenders']} similar users)")
    
    # Find items similar to a specific product
    similar_products = engine.find_similar_to(
        'iPhone',
        'Product',
        'PURCHASED',
        top_n=5
    )
    print("\nProducts similar to iPhone:")
    for p in similar_products:
        print(f"  {p['name']}: jaccard={p['jaccard']:.3f}")
    
finally:
    engine.close()
```

---

## Summary

### Algorithm Selection

| Need | Algorithm |
|------|-----------|
| Similar based on connections | Node Similarity |
| Similar based on properties | KNN |
| Custom similarity logic | Manual Cypher |
| Large-scale similarity | GDS with sampling |

### Key Parameters

| Algorithm | Important Parameters |
|-----------|---------------------|
| Node Similarity | topK, similarityCutoff, degreeCutoff |
| KNN | topK, nodeProperties, sampleRate, deltaThreshold |

---

## Exercises

### Exercise 28.1: Product Recommendations
1. Build a product purchase graph
2. Compute item-item similarity
3. Create a "frequently bought together" recommendation

### Exercise 28.2: User Segmentation
1. Calculate user-user similarity
2. Cluster similar users
3. Analyze segment characteristics

### Exercise 28.3: Hybrid Recommendations
1. Combine collaborative filtering with content-based
2. Weight different signals
3. Evaluate recommendation quality

---

**Next Chapter: [Chapter 29: Link Prediction](29-link-prediction.md)**
