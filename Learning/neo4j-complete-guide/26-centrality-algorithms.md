# Chapter 26: Centrality Algorithms Deep Dive

## Learning Objectives
By the end of this chapter, you will:
- Understand when to use each centrality measure
- Configure algorithms for optimal results
- Interpret centrality scores correctly
- Apply centrality to real business problems
- Combine multiple centrality measures

---

## 26.1 Overview of Centrality

### What Centrality Measures

Centrality answers: "Which nodes are most important?"

Different algorithms define "importance" differently:
- **Degree**: Who has the most connections?
- **PageRank**: Who is connected to important nodes?
- **Betweenness**: Who controls information flow?
- **Closeness**: Who can reach everyone quickly?
- **Eigenvector**: Who is influential in their network?

### When to Use Which

| Goal | Algorithm |
|------|-----------|
| Find connectors/hubs | Degree Centrality |
| Find influential nodes | PageRank, Eigenvector |
| Find gatekeepers/brokers | Betweenness Centrality |
| Find best broadcast points | Closeness Centrality |
| Find key actors (general) | Combine multiple |

---

## 26.2 Degree Centrality

### Concept

Simple count of connections (relationships).

### Types

- **In-Degree**: Incoming relationships
- **Out-Degree**: Outgoing relationships
- **Total Degree**: Both directions

### Implementation

```cypher
// Project graph
CALL gds.graph.project('social', 'Person', 'FOLLOWS')

// Total degree (undirected)
CALL gds.degree.stream('social', {orientation: 'UNDIRECTED'})
YIELD nodeId, score
RETURN gds.util.asNode(nodeId).name AS person, score AS connections
ORDER BY connections DESC

// In-degree (who has most followers)
CALL gds.degree.stream('social', {orientation: 'REVERSE'})
YIELD nodeId, score
RETURN gds.util.asNode(nodeId).name AS person, score AS followers
ORDER BY followers DESC

// Out-degree (who follows the most)
CALL gds.degree.stream('social', {orientation: 'NATURAL'})
YIELD nodeId, score
RETURN gds.util.asNode(nodeId).name AS person, score AS following
ORDER BY following DESC
```

### Weighted Degree

```cypher
// Project with weight
CALL gds.graph.project(
    'weightedSocial',
    'Person',
    {INTERACTS: {properties: 'weight'}}
)

// Weighted degree
CALL gds.degree.stream('weightedSocial', {
    relationshipWeightProperty: 'weight'
})
YIELD nodeId, score
RETURN gds.util.asNode(nodeId).name AS person, score AS weightedConnections
ORDER BY weightedConnections DESC
```

### Use Cases

- **Social Networks**: Find popular users
- **E-commerce**: Find most connected products
- **Citation Networks**: Find most cited papers

---

## 26.3 PageRank

### Concept

Nodes are important if connected to by other important nodes. Originally developed for Google Search.

### The Algorithm

```
PageRank(node) = (1-d) + d × Σ(PageRank(inbound) / outDegree(inbound))

Where d = damping factor (typically 0.85)
```

### Implementation

```cypher
// Basic PageRank
CALL gds.pageRank.stream('social', {
    maxIterations: 20,
    dampingFactor: 0.85
})
YIELD nodeId, score
RETURN gds.util.asNode(nodeId).name AS name, score
ORDER BY score DESC
LIMIT 10

// With tolerance (stop when converged)
CALL gds.pageRank.stream('social', {
    maxIterations: 50,
    dampingFactor: 0.85,
    tolerance: 0.0001
})
YIELD nodeId, score
RETURN gds.util.asNode(nodeId).name AS name, score
ORDER BY score DESC
```

### Weighted PageRank

```cypher
// Project with relationship weight
CALL gds.graph.project(
    'weightedNetwork',
    'Person',
    {KNOWS: {properties: 'strength'}}
)

// Weighted PageRank
CALL gds.pageRank.stream('weightedNetwork', {
    relationshipWeightProperty: 'strength',
    maxIterations: 20
})
YIELD nodeId, score
RETURN gds.util.asNode(nodeId).name, score
ORDER BY score DESC
```

### Personalized PageRank

Start from specific nodes:

```cypher
// PageRank from Alice's perspective
MATCH (source:Person {name: 'Alice'})
CALL gds.pageRank.stream('social', {
    sourceNodes: [source],
    maxIterations: 20
})
YIELD nodeId, score
WHERE score > 0.01
RETURN gds.util.asNode(nodeId).name AS name, score
ORDER BY score DESC

// Multiple source nodes
MATCH (source:Person) WHERE source.department = 'Engineering'
WITH collect(source) AS sources
CALL gds.pageRank.stream('social', {
    sourceNodes: sources,
    maxIterations: 20
})
YIELD nodeId, score
RETURN gds.util.asNode(nodeId).name, score
ORDER BY score DESC
```

### Use Cases

- **Web**: Rank web pages
- **Social**: Find influencers
- **Academic**: Important papers
- **Fraud**: Key entities in fraud rings

---

## 26.4 Betweenness Centrality

### Concept

Nodes that lie on many shortest paths between other nodes. They control information flow.

### Implementation

```cypher
// Basic betweenness
CALL gds.betweenness.stream('social')
YIELD nodeId, score
RETURN gds.util.asNode(nodeId).name AS name, score
ORDER BY score DESC

// Sampled betweenness (faster for large graphs)
CALL gds.betweenness.stream('social', {
    samplingSize: 1000,
    samplingSeed: 42
})
YIELD nodeId, score
RETURN gds.util.asNode(nodeId).name AS name, score
ORDER BY score DESC
```

### Normalized Betweenness

```cypher
// Get normalized scores
CALL gds.betweenness.stream('social')
YIELD nodeId, score
WITH gds.util.asNode(nodeId) AS node, score
WITH max(score) AS maxScore
MATCH (n:Person)
CALL gds.betweenness.stream('social')
YIELD nodeId, score
WHERE nodeId = id(n)
RETURN n.name, score, score/maxScore AS normalizedScore
ORDER BY normalizedScore DESC
```

### Use Cases

- **Organizations**: Find information brokers
- **Networks**: Identify critical infrastructure
- **Social**: Find bridge people between groups
- **Supply Chain**: Critical logistics points

---

## 26.5 Closeness Centrality

### Concept

How quickly a node can reach all other nodes. Low total distance = high closeness.

### Formula

```
Closeness(node) = (n-1) / Σ(shortest path distances)
```

### Implementation

```cypher
// Closeness centrality
CALL gds.closeness.stream('social')
YIELD nodeId, score
RETURN gds.util.asNode(nodeId).name AS name, score
ORDER BY score DESC

// Wasserman-Faust normalization (handles disconnected graphs)
CALL gds.closeness.stream('social', {
    useWassermanFaust: true
})
YIELD nodeId, score
RETURN gds.util.asNode(nodeId).name AS name, score
ORDER BY score DESC
```

### Harmonic Centrality

Better for disconnected graphs:

```cypher
CALL gds.closeness.harmonic.stream('social')
YIELD nodeId, score
RETURN gds.util.asNode(nodeId).name AS name, score
ORDER BY score DESC
```

### Use Cases

- **Emergency Response**: Best location for resources
- **Social**: Who spreads information fastest
- **Logistics**: Optimal warehouse locations

---

## 26.6 Eigenvector Centrality

### Concept

Similar to PageRank but without damping. Influence from connecting to influential nodes.

### Implementation

```cypher
CALL gds.eigenvector.stream('social', {
    maxIterations: 100,
    tolerance: 0.0001
})
YIELD nodeId, score
RETURN gds.util.asNode(nodeId).name AS name, score
ORDER BY score DESC
```

### Comparison with PageRank

```cypher
// Run both and compare
CALL gds.pageRank.stream('social')
YIELD nodeId, score AS pageRank
WITH collect({nodeId: nodeId, pageRank: pageRank}) AS prResults

CALL gds.eigenvector.stream('social')
YIELD nodeId, score AS eigenvector
WITH prResults, collect({nodeId: nodeId, eigenvector: eigenvector}) AS evResults

UNWIND prResults AS pr
UNWIND evResults AS ev
WHERE pr.nodeId = ev.nodeId
RETURN gds.util.asNode(pr.nodeId).name AS name,
       pr.pageRank,
       ev.eigenvector,
       abs(pr.pageRank - ev.eigenvector) AS difference
ORDER BY difference DESC
```

---

## 26.7 Article Rank

### Concept

Variant of PageRank that reduces impact of low-degree nodes.

```cypher
CALL gds.articleRank.stream('social', {
    dampingFactor: 0.85,
    maxIterations: 20
})
YIELD nodeId, score
RETURN gds.util.asNode(nodeId).name AS name, score
ORDER BY score DESC
```

---

## 26.8 HITS (Hubs and Authorities)

### Concept

Two scores per node:
- **Hub**: Points to good authorities
- **Authority**: Pointed to by good hubs

```cypher
CALL gds.hits.stream('webGraph', {
    hitsIterations: 20
})
YIELD nodeId, values
RETURN gds.util.asNode(nodeId).url AS page,
       values.hub AS hubScore,
       values.auth AS authorityScore
ORDER BY values.auth DESC
```

---

## 26.9 Combining Centrality Measures

### Multi-Metric Analysis

```cypher
// Calculate multiple centrality measures
CALL gds.pageRank.mutate('social', {mutateProperty: 'pageRank'})
CALL gds.betweenness.mutate('social', {mutateProperty: 'betweenness'})
CALL gds.degree.mutate('social', {mutateProperty: 'degree'})

// Query combined results
CALL gds.graph.nodeProperty.stream('social', 'pageRank')
YIELD nodeId, propertyValue AS pageRank
WITH nodeId, pageRank
CALL gds.graph.nodeProperty.stream('social', 'betweenness')
YIELD nodeId AS n2, propertyValue AS betweenness
WHERE n2 = nodeId
WITH nodeId, pageRank, betweenness
CALL gds.graph.nodeProperty.stream('social', 'degree')
YIELD nodeId AS n3, propertyValue AS degree
WHERE n3 = nodeId
RETURN gds.util.asNode(nodeId).name AS name,
       pageRank, betweenness, degree
ORDER BY pageRank DESC
```

### Composite Scoring

```python
from neo4j import GraphDatabase
import numpy as np
from sklearn.preprocessing import MinMaxScaler

def compute_composite_centrality(driver, graph_name: str):
    """Compute composite centrality score."""
    with driver.session() as session:
        # Get all centrality scores
        result = session.run("""
            CALL gds.pageRank.stream($graph) YIELD nodeId, score AS pageRank
            WITH collect({nodeId: nodeId, pageRank: pageRank}) AS pr
            CALL gds.betweenness.stream($graph) YIELD nodeId, score AS betweenness
            WITH pr, collect({nodeId: nodeId, betweenness: betweenness}) AS bt
            CALL gds.degree.stream($graph) YIELD nodeId, score AS degree
            WITH pr, bt, collect({nodeId: nodeId, degree: degree}) AS dg
            UNWIND pr AS p
            UNWIND bt AS b
            UNWIND dg AS d
            WHERE p.nodeId = b.nodeId AND b.nodeId = d.nodeId
            RETURN gds.util.asNode(p.nodeId).name AS name,
                   p.pageRank, b.betweenness, d.degree
        """, graph=graph_name)
        
        data = [dict(r) for r in result]
    
    if not data:
        return []
    
    # Normalize scores
    scaler = MinMaxScaler()
    metrics = ['pageRank', 'betweenness', 'degree']
    values = [[d[m] for m in metrics] for d in data]
    normalized = scaler.fit_transform(values)
    
    # Compute weighted composite
    weights = [0.4, 0.35, 0.25]  # Customize weights
    for i, d in enumerate(data):
        d['composite'] = sum(normalized[i][j] * weights[j] for j in range(3))
    
    return sorted(data, key=lambda x: x['composite'], reverse=True)
```

---

## 26.10 Python Complete Example

```python
from neo4j import GraphDatabase
from typing import List, Dict
import pandas as pd

URI = "neo4j://localhost:7687"
AUTH = ("neo4j", "password")

class CentralityAnalyzer:
    def __init__(self, uri, auth):
        self.driver = GraphDatabase.driver(uri, auth=auth)
    
    def close(self):
        self.driver.close()
    
    def project_graph(self, name: str, label: str, rel_type: str):
        """Project graph for analysis."""
        with self.driver.session() as session:
            session.run("CALL gds.graph.drop($name, false)", name=name)
            result = session.run("""
                CALL gds.graph.project($name, $label, $relType)
                YIELD nodeCount, relationshipCount
                RETURN nodeCount, relationshipCount
            """, name=name, label=label, relType=rel_type)
            return dict(result.single())
    
    def run_all_centralities(self, graph_name: str) -> pd.DataFrame:
        """Run all centrality algorithms and return DataFrame."""
        results = {}
        
        with self.driver.session() as session:
            # PageRank
            result = session.run("""
                CALL gds.pageRank.stream($graph)
                YIELD nodeId, score
                RETURN gds.util.asNode(nodeId).name AS name, score
            """, graph=graph_name)
            results['pageRank'] = {r['name']: r['score'] for r in result}
            
            # Betweenness
            result = session.run("""
                CALL gds.betweenness.stream($graph)
                YIELD nodeId, score
                RETURN gds.util.asNode(nodeId).name AS name, score
            """, graph=graph_name)
            results['betweenness'] = {r['name']: r['score'] for r in result}
            
            # Degree
            result = session.run("""
                CALL gds.degree.stream($graph)
                YIELD nodeId, score
                RETURN gds.util.asNode(nodeId).name AS name, score
            """, graph=graph_name)
            results['degree'] = {r['name']: r['score'] for r in result}
            
            # Closeness
            result = session.run("""
                CALL gds.closeness.stream($graph)
                YIELD nodeId, score
                RETURN gds.util.asNode(nodeId).name AS name, score
            """, graph=graph_name)
            results['closeness'] = {r['name']: r['score'] for r in result}
        
        # Combine into DataFrame
        names = set(results['pageRank'].keys())
        data = []
        for name in names:
            data.append({
                'name': name,
                'pageRank': results['pageRank'].get(name, 0),
                'betweenness': results['betweenness'].get(name, 0),
                'degree': results['degree'].get(name, 0),
                'closeness': results['closeness'].get(name, 0)
            })
        
        df = pd.DataFrame(data)
        
        # Add ranks
        for col in ['pageRank', 'betweenness', 'degree', 'closeness']:
            df[f'{col}_rank'] = df[col].rank(ascending=False)
        
        return df.sort_values('pageRank', ascending=False)
    
    def find_key_players(self, graph_name: str, top_n: int = 10) -> List[Dict]:
        """Find key players based on multiple centrality measures."""
        df = self.run_all_centralities(graph_name)
        
        # Normalize and compute composite score
        for col in ['pageRank', 'betweenness', 'degree', 'closeness']:
            max_val = df[col].max()
            if max_val > 0:
                df[f'{col}_norm'] = df[col] / max_val
        
        # Weighted composite
        df['composite'] = (
            df['pageRank_norm'] * 0.3 +
            df['betweenness_norm'] * 0.25 +
            df['degree_norm'] * 0.25 +
            df['closeness_norm'] * 0.2
        )
        
        return df.nlargest(top_n, 'composite').to_dict('records')
    
    def identify_roles(self, graph_name: str) -> Dict[str, List[str]]:
        """Identify node roles based on centrality profiles."""
        df = self.run_all_centralities(graph_name)
        
        # Normalize
        for col in ['pageRank', 'betweenness', 'degree', 'closeness']:
            max_val = df[col].max()
            if max_val > 0:
                df[f'{col}_norm'] = df[col] / max_val
        
        roles = {
            'influencers': [],      # High PageRank
            'brokers': [],          # High Betweenness
            'hubs': [],             # High Degree
            'broadcasters': [],     # High Closeness
            'peripheral': []        # Low all
        }
        
        for _, row in df.iterrows():
            if row.get('pageRank_norm', 0) > 0.7:
                roles['influencers'].append(row['name'])
            if row.get('betweenness_norm', 0) > 0.7:
                roles['brokers'].append(row['name'])
            if row.get('degree_norm', 0) > 0.7:
                roles['hubs'].append(row['name'])
            if row.get('closeness_norm', 0) > 0.7:
                roles['broadcasters'].append(row['name'])
            
            # Check if peripheral (low on all)
            if all(row.get(f'{c}_norm', 0) < 0.2 
                   for c in ['pageRank', 'betweenness', 'degree', 'closeness']):
                roles['peripheral'].append(row['name'])
        
        return roles

# Usage
analyzer = CentralityAnalyzer(URI, AUTH)
try:
    # Project graph
    stats = analyzer.project_graph('social', 'Person', 'KNOWS')
    print(f"Projected graph: {stats}")
    
    # Run all centralities
    df = analyzer.run_all_centralities('social')
    print("\nCentrality Analysis:")
    print(df.head(10).to_string())
    
    # Find key players
    key_players = analyzer.find_key_players('social', top_n=5)
    print("\nTop 5 Key Players:")
    for p in key_players:
        print(f"  {p['name']}: composite={p['composite']:.4f}")
    
    # Identify roles
    roles = analyzer.identify_roles('social')
    print("\nIdentified Roles:")
    for role, members in roles.items():
        if members:
            print(f"  {role}: {', '.join(members[:5])}")
            
finally:
    analyzer.close()
```

---

## Summary

### Centrality Algorithm Selection Guide

| Question | Best Algorithm |
|----------|---------------|
| Who has most connections? | Degree |
| Who is influential? | PageRank |
| Who bridges communities? | Betweenness |
| Who can spread info fastest? | Closeness |
| Who is influential through connections? | Eigenvector |

### Key Parameters

| Algorithm | Key Parameters |
|-----------|---------------|
| PageRank | dampingFactor, maxIterations, tolerance |
| Betweenness | samplingSize (for large graphs) |
| Closeness | useWassermanFaust (disconnected graphs) |
| Degree | orientation (NATURAL, REVERSE, UNDIRECTED) |

---

## Exercises

### Exercise 26.1: Social Network Analysis
1. Load a social network dataset
2. Compute all centrality measures
3. Identify the top 10 most important users by each measure

### Exercise 26.2: Role Identification
1. Create a categorization system based on centrality profiles
2. Identify influencers, brokers, and peripheral nodes
3. Validate findings against known data

### Exercise 26.3: Weighted Analysis
1. Add relationship weights (interaction frequency)
2. Compare weighted vs unweighted centrality
3. Analyze how weights affect rankings

---

**Next Chapter: [Chapter 27: Community Detection Algorithms](27-community-detection.md)**
