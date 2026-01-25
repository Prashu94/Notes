# Chapter 29: Link Prediction

## Learning Objectives
By the end of this chapter, you will:
- Understand link prediction fundamentals
- Apply link prediction algorithms
- Build ML pipelines for link prediction
- Evaluate prediction quality
- Use link prediction for recommendations

---

## 29.1 Introduction to Link Prediction

### What is Link Prediction?

Link prediction estimates the likelihood of a connection forming between two nodes that are not currently connected.

### Applications

| Domain | Prediction |
|--------|------------|
| Social Networks | Friend recommendations |
| E-commerce | Product associations |
| Biology | Protein interactions |
| Knowledge Graphs | Missing facts |
| Fraud Detection | Suspicious relationships |

### Approaches

1. **Heuristic-based**: Common Neighbors, Preferential Attachment
2. **Similarity-based**: Jaccard, Cosine similarity
3. **Path-based**: Katz index, Random Walk
4. **Embedding-based**: Node2Vec, GraphSAGE
5. **ML Pipeline**: GDS Link Prediction Pipeline

---

## 29.2 Heuristic Link Prediction

### Common Neighbors

Nodes with many shared neighbors are likely to connect:

```cypher
// Find pairs with most common neighbors
MATCH (p1:Person)-[:KNOWS]->(common)<-[:KNOWS]-(p2:Person)
WHERE p1 <> p2 AND NOT (p1)-[:KNOWS]-(p2)
WITH p1, p2, count(DISTINCT common) AS commonNeighbors
WHERE commonNeighbors > 2
RETURN p1.name AS person1, p2.name AS person2, commonNeighbors
ORDER BY commonNeighbors DESC
LIMIT 20

// Using GDS function
MATCH (p1:Person {name: 'Alice'}), (p2:Person {name: 'Bob'})
WHERE NOT (p1)-[:KNOWS]-(p2)
RETURN gds.alpha.linkprediction.commonNeighbors(p1, p2) AS score
```

### Preferential Attachment

Popular nodes tend to attract more connections:

```cypher
// Score = degree(A) × degree(B)
MATCH (p1:Person), (p2:Person)
WHERE p1 <> p2 AND NOT (p1)-[:KNOWS]-(p2)
WITH p1, p2,
     size((p1)-[:KNOWS]-()) AS degree1,
     size((p2)-[:KNOWS]-()) AS degree2
RETURN p1.name, p2.name, 
       degree1 * degree2 AS preferentialAttachment
ORDER BY preferentialAttachment DESC
LIMIT 20

// Using GDS function
MATCH (p1:Person {name: 'Alice'}), (p2:Person {name: 'Bob'})
RETURN gds.alpha.linkprediction.preferentialAttachment(p1, p2) AS score
```

### Adamic-Adar Index

Weights common neighbors by their specificity (rare connections are more valuable):

```cypher
// Score = Σ(1 / log(degree(common)))
MATCH (p1:Person)-[:KNOWS]->(common)<-[:KNOWS]-(p2:Person)
WHERE p1 <> p2 AND NOT (p1)-[:KNOWS]-(p2)
WITH p1, p2, common, size((common)-[:KNOWS]-()) AS commonDegree
WHERE commonDegree > 1
WITH p1, p2, sum(1.0 / log(commonDegree)) AS adamicAdar
RETURN p1.name, p2.name, adamicAdar
ORDER BY adamicAdar DESC
LIMIT 20

// Using GDS function
MATCH (p1:Person {name: 'Alice'}), (p2:Person {name: 'Bob'})
RETURN gds.alpha.linkprediction.adamicAdar(p1, p2) AS score
```

### Resource Allocation Index

Similar to Adamic-Adar but with different weighting:

```cypher
// Score = Σ(1 / degree(common))
MATCH (p1:Person)-[:KNOWS]->(common)<-[:KNOWS]-(p2:Person)
WHERE p1 <> p2 AND NOT (p1)-[:KNOWS]-(p2)
WITH p1, p2, common, size((common)-[:KNOWS]-()) AS commonDegree
WHERE commonDegree > 0
WITH p1, p2, sum(1.0 / commonDegree) AS resourceAllocation
RETURN p1.name, p2.name, resourceAllocation
ORDER BY resourceAllocation DESC
LIMIT 20

// Using GDS function
MATCH (p1:Person {name: 'Alice'}), (p2:Person {name: 'Bob'})
RETURN gds.alpha.linkprediction.resourceAllocation(p1, p2) AS score
```

### Total Neighbors

Union of all neighbors:

```cypher
// Using GDS function
MATCH (p1:Person {name: 'Alice'}), (p2:Person {name: 'Bob'})
RETURN gds.alpha.linkprediction.totalNeighbors(p1, p2) AS totalNeighbors
```

---

## 29.3 Similarity-Based Prediction

### Jaccard-Based Link Prediction

```cypher
// Predict links based on Jaccard similarity of neighborhoods
MATCH (p1:Person)-[:KNOWS]->(neighbor)
WITH p1, collect(id(neighbor)) AS neighbors1
MATCH (p2:Person)-[:KNOWS]->(neighbor)
WHERE p1 <> p2 AND NOT (p1)-[:KNOWS]-(p2)
WITH p1, neighbors1, p2, collect(id(neighbor)) AS neighbors2
RETURN p1.name, p2.name,
       gds.similarity.jaccard(neighbors1, neighbors2) AS jaccardScore
ORDER BY jaccardScore DESC
LIMIT 20
```

### Node Similarity for Link Prediction

```cypher
// Project graph
CALL gds.graph.project('social', 'Person', 'KNOWS')

// Find potential new links
CALL gds.nodeSimilarity.stream('social', {
    topK: 10,
    similarityCutoff: 0.3
})
YIELD node1, node2, similarity
WITH gds.util.asNode(node1) AS p1, gds.util.asNode(node2) AS p2, similarity
WHERE NOT (p1)-[:KNOWS]-(p2)
RETURN p1.name AS person1, p2.name AS person2, similarity AS linkProbability
ORDER BY linkProbability DESC
```

---

## 29.4 Path-Based Prediction

### Katz Index

Counts paths of all lengths with exponential decay:

```cypher
// Simplified Katz-like score (paths up to length 3)
MATCH (p1:Person {name: 'Alice'}), (p2:Person {name: 'Bob'})
WHERE NOT (p1)-[:KNOWS]-(p2)

// Count paths of different lengths
OPTIONAL MATCH path2 = (p1)-[:KNOWS*2]-(p2)
WITH p1, p2, count(path2) AS paths2
OPTIONAL MATCH path3 = (p1)-[:KNOWS*3]-(p2)
WITH p1, p2, paths2, count(path3) AS paths3

// Apply decay (beta = 0.5)
RETURN p1.name, p2.name,
       paths2 * 0.25 + paths3 * 0.125 AS katzScore
```

### Random Walk with Restart

```cypher
// Personalized PageRank as link predictor
MATCH (source:Person {name: 'Alice'})
CALL gds.pageRank.stream('social', {
    sourceNodes: [source],
    maxIterations: 20,
    dampingFactor: 0.85
})
YIELD nodeId, score
WITH gds.util.asNode(nodeId) AS target, score
WHERE NOT (source)-[:KNOWS]-(target) AND source <> target
RETURN target.name, score AS linkProbability
ORDER BY score DESC
LIMIT 10
```

---

## 29.5 GDS Link Prediction Pipeline

### Pipeline Overview

The GDS Link Prediction Pipeline provides end-to-end ML-based link prediction.

### Step 1: Create Pipeline

```cypher
// Create a new pipeline
CALL gds.beta.pipeline.linkPrediction.create('myLinkPredictionPipeline')
```

### Step 2: Add Features

```cypher
// Add link features
CALL gds.beta.pipeline.linkPrediction.addFeature('myLinkPredictionPipeline', 'hadamard', {
    nodeProperties: ['embedding']
})

CALL gds.beta.pipeline.linkPrediction.addFeature('myLinkPredictionPipeline', 'cosine', {
    nodeProperties: ['embedding']
})

CALL gds.beta.pipeline.linkPrediction.addFeature('myLinkPredictionPipeline', 'l2', {
    nodeProperties: ['embedding']
})

// Add standard link prediction features
CALL gds.beta.pipeline.linkPrediction.addFeature('myLinkPredictionPipeline', 'commonNeighbors', {})
CALL gds.beta.pipeline.linkPrediction.addFeature('myLinkPredictionPipeline', 'adamicAdar', {})
CALL gds.beta.pipeline.linkPrediction.addFeature('myLinkPredictionPipeline', 'preferentialAttachment', {})
```

### Step 3: Configure Training

```cypher
// Add node property steps (e.g., compute embeddings)
CALL gds.beta.pipeline.linkPrediction.addNodeProperty('myLinkPredictionPipeline', 'fastRP', {
    embeddingDimension: 128,
    mutateProperty: 'embedding'
})

// Configure split
CALL gds.beta.pipeline.linkPrediction.configureSplit('myLinkPredictionPipeline', {
    testFraction: 0.2,
    trainFraction: 0.8,
    validationFolds: 5,
    negativeSamplingRatio: 1.0
})
```

### Step 4: Add Model Candidates

```cypher
// Add logistic regression
CALL gds.beta.pipeline.linkPrediction.addLogisticRegression('myLinkPredictionPipeline', {
    penalty: 0.001,
    maxEpochs: 500
})

// Add random forest
CALL gds.beta.pipeline.linkPrediction.addRandomForest('myLinkPredictionPipeline', {
    numberOfDecisionTrees: 100,
    maxDepth: 5
})
```

### Step 5: Train Pipeline

```cypher
// Project graph with relationships
CALL gds.graph.project(
    'socialForLinkPrediction',
    'Person',
    {KNOWS: {orientation: 'UNDIRECTED'}}
)

// Train the pipeline
CALL gds.beta.pipeline.linkPrediction.train('socialForLinkPrediction', {
    pipeline: 'myLinkPredictionPipeline',
    modelName: 'friendPredictionModel',
    targetRelationshipType: 'KNOWS',
    metrics: ['AUCPR', 'OUT_OF_BAG_ERROR'],
    randomSeed: 42
})
YIELD modelInfo, modelSelectionStats
RETURN modelInfo.bestParameters AS bestParams,
       modelSelectionStats.validationStats AS validationStats
```

### Step 6: Make Predictions

```cypher
// Predict new links
CALL gds.beta.pipeline.linkPrediction.predict.stream('socialForLinkPrediction', {
    modelName: 'friendPredictionModel',
    topN: 100,
    threshold: 0.5
})
YIELD node1, node2, probability
RETURN gds.util.asNode(node1).name AS person1,
       gds.util.asNode(node2).name AS person2,
       probability
ORDER BY probability DESC
```

---

## 29.6 Evaluation Metrics

### Split Data for Evaluation

```cypher
// Create test set by hiding some relationships
CALL gds.graph.relationships.split.mutate('social', {
    relationshipType: 'KNOWS',
    holdoutFraction: 0.2,
    negativeSamplingRatio: 1.0,
    randomSeed: 42
})
YIELD relationshipsWritten, holdoutRelationshipsWritten
```

### Metrics

| Metric | Description |
|--------|-------------|
| **AUROC** | Area Under ROC Curve |
| **AUCPR** | Area Under Precision-Recall Curve |
| **Precision@K** | Precision in top K predictions |
| **Recall@K** | Recall in top K predictions |
| **MRR** | Mean Reciprocal Rank |

### Manual Evaluation

```cypher
// Simple precision calculation
// Assume we have predictions with probabilities
WITH [
    {person1: 'Alice', person2: 'Bob', probability: 0.9},
    {person1: 'Alice', person2: 'Carol', probability: 0.8},
    {person1: 'Bob', person2: 'Dave', probability: 0.7}
] AS predictions

// Check against actual new connections
UNWIND predictions AS pred
MATCH (p1:Person {name: pred.person1}), (p2:Person {name: pred.person2})
OPTIONAL MATCH (p1)-[actual:KNOWS]-(p2)
WITH pred, actual IS NOT NULL AS correct
RETURN count(*) AS totalPredictions,
       sum(CASE WHEN correct THEN 1 ELSE 0 END) AS correctPredictions,
       toFloat(sum(CASE WHEN correct THEN 1 ELSE 0 END)) / count(*) AS precision
```

---

## 29.7 Temporal Link Prediction

### Time-Aware Features

```cypher
// Consider relationship timing
MATCH (p1:Person)-[r1:KNOWS]->(common)<-[r2:KNOWS]-(p2:Person)
WHERE p1 <> p2 AND NOT (p1)-[:KNOWS]-(p2)
WITH p1, p2, common,
     // Recent connections weighted higher
     CASE WHEN r1.since > date() - duration({months: 6}) THEN 2 ELSE 1 END AS weight1,
     CASE WHEN r2.since > date() - duration({months: 6}) THEN 2 ELSE 1 END AS weight2
WITH p1, p2, sum(weight1 * weight2) AS timeWeightedScore
RETURN p1.name, p2.name, timeWeightedScore
ORDER BY timeWeightedScore DESC
LIMIT 20
```

### Growth Patterns

```cypher
// Predict links based on growth trajectory
MATCH (p:Person)
WHERE p.joinDate IS NOT NULL
WITH p, duration.between(p.joinDate, date()).months AS accountAge,
     size((p)-[:KNOWS]-()) AS connections
WITH p, 
     connections * 1.0 / CASE WHEN accountAge = 0 THEN 1 ELSE accountAge END AS growthRate

// Find fast-growing users
WITH p, growthRate
ORDER BY growthRate DESC
LIMIT 50

// Predict connections between fast-growing users
MATCH (p), (other:Person)
WHERE p <> other 
  AND NOT (p)-[:KNOWS]-(other)
  AND other.growthRate > 5
RETURN p.name, other.name, p.growthRate + other.growthRate AS combinedGrowth
ORDER BY combinedGrowth DESC
LIMIT 20
```

---

## 29.8 Domain-Specific Link Prediction

### Social Network Friend Suggestions

```cypher
// Combine multiple signals
MATCH (target:Person {name: 'Alice'})

// Score potential friends
MATCH (candidate:Person)
WHERE target <> candidate AND NOT (target)-[:KNOWS]-(candidate)

// Common friends
OPTIONAL MATCH (target)-[:KNOWS]-(mutual)-[:KNOWS]-(candidate)
WITH target, candidate, count(DISTINCT mutual) AS mutualFriends

// Same interests
OPTIONAL MATCH (target)-[:INTERESTED_IN]->(interest)<-[:INTERESTED_IN]-(candidate)
WITH target, candidate, mutualFriends, count(DISTINCT interest) AS commonInterests

// Same location
WITH target, candidate, mutualFriends, commonInterests,
     CASE WHEN target.city = candidate.city THEN 1 ELSE 0 END AS sameCity

// Same workplace
OPTIONAL MATCH (target)-[:WORKS_AT]->(company)<-[:WORKS_AT]-(candidate)
WITH target, candidate, mutualFriends, commonInterests, sameCity,
     CASE WHEN company IS NOT NULL THEN 1 ELSE 0 END AS sameCompany

// Weighted score
RETURN candidate.name AS suggestion,
       mutualFriends,
       commonInterests,
       sameCity,
       sameCompany,
       mutualFriends * 3 + 
       commonInterests * 2 + 
       sameCity * 1 + 
       sameCompany * 2 AS score
ORDER BY score DESC
LIMIT 10
```

### Knowledge Graph Completion

```cypher
// Predict missing relationships in knowledge graph
// Type: Person -[WORKS_AT]-> Company

MATCH (p:Person)-[:LIVES_IN]->(:City)<-[:LOCATED_IN]-(c:Company)
WHERE NOT (p)-[:WORKS_AT]->(c)

// Check if similar people work there
OPTIONAL MATCH (p)-[:GRADUATED_FROM]->(:University)<-[:GRADUATED_FROM]-(colleague)-[:WORKS_AT]->(c)
WITH p, c, count(DISTINCT colleague) AS alumniAtCompany

// Check skills match
OPTIONAL MATCH (p)-[:HAS_SKILL]->(skill)<-[:REQUIRES]-(c)
WITH p, c, alumniAtCompany, count(DISTINCT skill) AS matchingSkills

RETURN p.name AS person,
       c.name AS company,
       alumniAtCompany,
       matchingSkills,
       alumniAtCompany * 2 + matchingSkills * 3 AS likelihood
ORDER BY likelihood DESC
LIMIT 20
```

---

## 29.9 Python Integration

```python
from neo4j import GraphDatabase
from typing import List, Dict, Tuple
import numpy as np
from sklearn.metrics import roc_auc_score, precision_recall_curve, auc

URI = "neo4j://localhost:7687"
AUTH = ("neo4j", "password")

class LinkPredictor:
    def __init__(self, uri, auth):
        self.driver = GraphDatabase.driver(uri, auth=auth)
    
    def close(self):
        self.driver.close()
    
    def compute_common_neighbors(self, node1_name: str, 
                                  node2_name: str) -> int:
        """Compute common neighbors score."""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (p1:Person {name: $n1})-[:KNOWS]->(common)<-[:KNOWS]-(p2:Person {name: $n2})
                RETURN count(DISTINCT common) AS score
            """, n1=node1_name, n2=node2_name)
            return result.single()['score']
    
    def compute_adamic_adar(self, node1_name: str, 
                            node2_name: str) -> float:
        """Compute Adamic-Adar index."""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (p1:Person {name: $n1})-[:KNOWS]->(common)<-[:KNOWS]-(p2:Person {name: $n2})
                WITH common, size((common)-[:KNOWS]-()) AS degree
                WHERE degree > 1
                RETURN sum(1.0 / log(degree)) AS score
            """, n1=node1_name, n2=node2_name)
            record = result.single()
            return record['score'] if record['score'] else 0.0
    
    def predict_links_heuristic(self, source_name: str, 
                                 top_n: int = 10) -> List[Dict]:
        """Predict links using combined heuristics."""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (source:Person {name: $name})
                MATCH (candidate:Person)
                WHERE source <> candidate AND NOT (source)-[:KNOWS]-(candidate)
                
                // Common neighbors
                OPTIONAL MATCH (source)-[:KNOWS]->(common)<-[:KNOWS]-(candidate)
                WITH source, candidate, count(DISTINCT common) AS cn
                
                // Preferential attachment
                WITH source, candidate, cn,
                     size((source)-[:KNOWS]-()) * size((candidate)-[:KNOWS]-()) AS pa
                
                // Adamic-Adar
                OPTIONAL MATCH (source)-[:KNOWS]->(common2)<-[:KNOWS]-(candidate)
                WITH source, candidate, cn, pa, common2, 
                     size((common2)-[:KNOWS]-()) AS commonDegree
                WHERE commonDegree > 1 OR common2 IS NULL
                WITH source, candidate, cn, pa,
                     sum(CASE WHEN common2 IS NOT NULL THEN 1.0/log(commonDegree) ELSE 0 END) AS aa
                
                // Combined score
                RETURN candidate.name AS prediction,
                       cn AS commonNeighbors,
                       pa AS preferentialAttachment,
                       aa AS adamicAdar,
                       cn * 0.4 + pa * 0.0001 + aa * 0.3 AS combinedScore
                ORDER BY combinedScore DESC
                LIMIT $limit
            """, name=source_name, limit=top_n)
            
            return [dict(r) for r in result]
    
    def predict_links_embedding(self, graph_name: str,
                                 top_n: int = 100) -> List[Dict]:
        """Predict links using embedding similarity."""
        with self.driver.session() as session:
            # First create embeddings
            session.run(f"""
                CALL gds.fastRP.mutate('{graph_name}', {{
                    embeddingDimension: 128,
                    mutateProperty: 'embedding'
                }})
            """)
            
            # Use KNN for link prediction
            result = session.run(f"""
                CALL gds.knn.stream('{graph_name}', {{
                    topK: 10,
                    nodeProperties: ['embedding']
                }})
                YIELD node1, node2, similarity
                WITH gds.util.asNode(node1) AS p1, 
                     gds.util.asNode(node2) AS p2, 
                     similarity
                WHERE NOT (p1)-[:KNOWS]-(p2)
                RETURN p1.name AS person1, 
                       p2.name AS person2, 
                       similarity AS probability
                ORDER BY probability DESC
                LIMIT $limit
            """, limit=top_n)
            
            return [dict(r) for r in result]
    
    def evaluate_predictions(self, predictions: List[Tuple[str, str, float]],
                             actuals: List[Tuple[str, str]]) -> Dict:
        """Evaluate link prediction quality."""
        # Convert actuals to set for fast lookup
        actual_set = set(actuals)
        
        # Create labels and scores
        y_true = []
        y_scores = []
        
        for person1, person2, prob in predictions:
            y_scores.append(prob)
            # Check if this link exists (in either direction)
            exists = (person1, person2) in actual_set or (person2, person1) in actual_set
            y_true.append(1 if exists else 0)
        
        if sum(y_true) == 0:
            return {'error': 'No positive samples in evaluation set'}
        
        # Calculate metrics
        auroc = roc_auc_score(y_true, y_scores)
        precision, recall, _ = precision_recall_curve(y_true, y_scores)
        auprc = auc(recall, precision)
        
        # Precision@K
        k_values = [10, 20, 50]
        precision_at_k = {}
        for k in k_values:
            top_k = sorted(zip(y_true, y_scores), key=lambda x: x[1], reverse=True)[:k]
            precision_at_k[f'P@{k}'] = sum(1 for y, _ in top_k if y == 1) / k
        
        return {
            'AUROC': auroc,
            'AUPRC': auprc,
            **precision_at_k,
            'total_predictions': len(predictions),
            'positive_samples': sum(y_true)
        }
    
    def train_pipeline(self, graph_name: str, 
                       pipeline_name: str,
                       model_name: str) -> Dict:
        """Train a GDS link prediction pipeline."""
        with self.driver.session() as session:
            # Create pipeline
            session.run(f"CALL gds.beta.pipeline.linkPrediction.create('{pipeline_name}')")
            
            # Add node property step
            session.run(f"""
                CALL gds.beta.pipeline.linkPrediction.addNodeProperty('{pipeline_name}', 'fastRP', {{
                    embeddingDimension: 64,
                    mutateProperty: 'embedding'
                }})
            """)
            
            # Add features
            session.run(f"""
                CALL gds.beta.pipeline.linkPrediction.addFeature('{pipeline_name}', 'hadamard', {{
                    nodeProperties: ['embedding']
                }})
            """)
            session.run(f"CALL gds.beta.pipeline.linkPrediction.addFeature('{pipeline_name}', 'commonNeighbors', {{}})")
            
            # Configure split
            session.run(f"""
                CALL gds.beta.pipeline.linkPrediction.configureSplit('{pipeline_name}', {{
                    testFraction: 0.2,
                    trainFraction: 0.8,
                    validationFolds: 3
                }})
            """)
            
            # Add model
            session.run(f"""
                CALL gds.beta.pipeline.linkPrediction.addLogisticRegression('{pipeline_name}', {{
                    penalty: 0.01
                }})
            """)
            
            # Train
            result = session.run(f"""
                CALL gds.beta.pipeline.linkPrediction.train('{graph_name}', {{
                    pipeline: '{pipeline_name}',
                    modelName: '{model_name}',
                    targetRelationshipType: 'KNOWS',
                    metrics: ['AUCPR']
                }})
                YIELD modelInfo
                RETURN modelInfo.metrics AS metrics
            """)
            
            return dict(result.single())

# Usage
predictor = LinkPredictor(URI, AUTH)
try:
    # Heuristic-based predictions
    predictions = predictor.predict_links_heuristic('Alice', top_n=10)
    print("Link predictions for Alice:")
    for p in predictions:
        print(f"  -> {p['prediction']}: score={p['combinedScore']:.4f}")
        print(f"     (CN={p['commonNeighbors']}, PA={p['preferentialAttachment']}, AA={p['adamicAdar']:.3f})")
    
    # Individual metrics
    cn = predictor.compute_common_neighbors('Alice', 'Bob')
    aa = predictor.compute_adamic_adar('Alice', 'Bob')
    print(f"\nAlice-Bob metrics:")
    print(f"  Common Neighbors: {cn}")
    print(f"  Adamic-Adar: {aa:.4f}")
    
finally:
    predictor.close()
```

---

## Summary

### Algorithm Selection

| Approach | Best For | Speed |
|----------|----------|-------|
| Common Neighbors | Dense networks | Fast |
| Preferential Attachment | Scale-free networks | Fast |
| Adamic-Adar | Weighted by specificity | Fast |
| Node Similarity | Bipartite graphs | Medium |
| Embedding-based | Complex patterns | Slow |
| ML Pipeline | Production systems | Slow |

### Key Formulas

| Method | Formula |
|--------|---------|
| Common Neighbors | \|N(x) ∩ N(y)\| |
| Preferential Attachment | \|N(x)\| × \|N(y)\| |
| Adamic-Adar | Σ 1/log(\|N(z)\|) for z ∈ N(x) ∩ N(y) |
| Jaccard | \|N(x) ∩ N(y)\| / \|N(x) ∪ N(y)\| |

---

## Exercises

### Exercise 29.1: Friend Recommendations
1. Build a social network graph
2. Implement multiple link prediction methods
3. Compare and combine their results

### Exercise 29.2: ML Pipeline
1. Create a GDS link prediction pipeline
2. Train with different feature combinations
3. Evaluate on held-out test set

### Exercise 29.3: Temporal Prediction
1. Add timestamps to relationships
2. Predict links based on temporal patterns
3. Evaluate prediction accuracy over time

---

**Next Chapter: [Chapter 30: Vector Search and Embeddings](30-vector-search.md)**
