# Chapter 27: Community Detection Algorithms

## Learning Objectives
By the end of this chapter, you will:
- Understand different community detection approaches
- Apply Louvain, Label Propagation, and WCC algorithms
- Detect hierarchical community structures
- Evaluate community quality
- Build community-based features for ML

---

## 27.1 What is Community Detection?

### Definition

Community detection finds groups of nodes that are:
- **Densely connected** internally
- **Sparsely connected** to other groups

### Applications

- **Social Networks**: Friend groups, interest communities
- **Biology**: Protein complexes, gene networks
- **Fraud Detection**: Collusion rings
- **Marketing**: Customer segments
- **E-commerce**: Product categories

### Algorithm Categories

| Category | Algorithm | Best For |
|----------|-----------|----------|
| Modularity-based | Louvain | Quality communities |
| Propagation | Label Propagation | Speed |
| Component-based | WCC, SCC | Connectivity |
| Hierarchical | Leiden | Nested communities |
| Spectral | K-1 Coloring | Graph partitioning |

---

## 27.2 Louvain Algorithm

### How It Works

1. Assign each node to its own community
2. Move nodes to neighboring communities to maximize modularity
3. Aggregate communities into single nodes
4. Repeat until no improvement

### Modularity

```
Q = (1/2m) × Σ[(Aij - kikj/2m) × δ(ci, cj)]

Where:
- Aij = edge weight between i and j
- ki = degree of node i
- m = total edges
- δ = 1 if same community, 0 otherwise
```

### Implementation

```cypher
// Create graph projection
CALL gds.graph.project('socialNetwork', 'Person', 'KNOWS')

// Basic Louvain
CALL gds.louvain.stream('socialNetwork')
YIELD nodeId, communityId
RETURN communityId, 
       count(*) AS size,
       collect(gds.util.asNode(nodeId).name) AS members
ORDER BY size DESC

// With statistics
CALL gds.louvain.stats('socialNetwork')
YIELD communityCount, modularity, ranLevels, communityDistribution
RETURN *

// Write to database
CALL gds.louvain.write('socialNetwork', {
    writeProperty: 'community'
})
YIELD communityCount, modularity, nodePropertiesWritten
```

### Configuration Options

```cypher
// Weighted communities
CALL gds.graph.project(
    'weightedSocial',
    'Person',
    {KNOWS: {properties: 'strength'}}
)

CALL gds.louvain.stream('weightedSocial', {
    relationshipWeightProperty: 'strength',
    maxLevels: 10,
    maxIterations: 10,
    tolerance: 0.0001,
    includeIntermediateCommunities: true,
    consecutiveIds: true
})
YIELD nodeId, communityId, intermediateCommunityIds
RETURN gds.util.asNode(nodeId).name AS name,
       communityId AS finalCommunity,
       intermediateCommunityIds AS hierarchy

// Seeded communities (start with existing assignments)
CALL gds.louvain.stream('socialNetwork', {
    seedProperty: 'existingCommunity'
})
YIELD nodeId, communityId
RETURN *
```

### Hierarchical Communities

```cypher
// Get intermediate communities
CALL gds.louvain.stream('socialNetwork', {
    includeIntermediateCommunities: true
})
YIELD nodeId, communityId, intermediateCommunityIds
WITH gds.util.asNode(nodeId) AS person, 
     communityId, 
     intermediateCommunityIds
RETURN person.name,
       intermediateCommunityIds[0] AS level1,
       intermediateCommunityIds[1] AS level2,
       communityId AS finalLevel
ORDER BY finalLevel, level1
```

---

## 27.3 Label Propagation

### How It Works

1. Assign unique label to each node
2. Each node adopts most common label among neighbors
3. Repeat until convergence

### Characteristics

- **Very fast** - near-linear time
- **Non-deterministic** - different runs may produce different results
- **Good for large graphs**

### Implementation

```cypher
// Basic Label Propagation
CALL gds.labelPropagation.stream('socialNetwork')
YIELD nodeId, communityId
RETURN communityId, 
       count(*) AS size,
       collect(gds.util.asNode(nodeId).name) AS members
ORDER BY size DESC

// With max iterations
CALL gds.labelPropagation.stream('socialNetwork', {
    maxIterations: 10,
    consecutiveIds: true
})
YIELD nodeId, communityId
RETURN communityId, count(*) AS size
ORDER BY size DESC

// Seeded Label Propagation
CALL gds.labelPropagation.stream('socialNetwork', {
    seedProperty: 'department'
})
YIELD nodeId, communityId
RETURN gds.util.asNode(nodeId).name, communityId

// Write results
CALL gds.labelPropagation.write('socialNetwork', {
    writeProperty: 'lpCommunity',
    maxIterations: 10
})
YIELD communityCount, ranIterations, didConverge
```

### Weighted Label Propagation

```cypher
// Node weights (influence)
CALL gds.graph.project(
    'weightedNodes',
    {Person: {properties: 'influence'}},
    'KNOWS'
)

CALL gds.labelPropagation.stream('weightedNodes', {
    nodeWeightProperty: 'influence'
})
YIELD nodeId, communityId
RETURN communityId, count(*) AS size

// Relationship weights
CALL gds.labelPropagation.stream('weightedSocial', {
    relationshipWeightProperty: 'strength'
})
YIELD nodeId, communityId
RETURN communityId, count(*) AS size
```

---

## 27.4 Weakly Connected Components (WCC)

### What It Finds

Groups of nodes where every node can reach every other node, ignoring direction.

### Implementation

```cypher
// Find all components
CALL gds.wcc.stream('socialNetwork')
YIELD nodeId, componentId
RETURN componentId, 
       count(*) AS size,
       collect(gds.util.asNode(nodeId).name) AS members
ORDER BY size DESC

// Statistics
CALL gds.wcc.stats('socialNetwork')
YIELD componentCount, componentDistribution
RETURN componentCount, componentDistribution

// Write components
CALL gds.wcc.write('socialNetwork', {
    writeProperty: 'componentId'
})
YIELD componentCount, nodePropertiesWritten

// Seeded WCC (connect to existing component)
CALL gds.wcc.stream('socialNetwork', {
    seedProperty: 'existingComponent'
})
YIELD nodeId, componentId
RETURN componentId, count(*) AS size
```

### Use Cases

- Find disconnected subgraphs
- Pre-processing for other algorithms
- Data quality checks

---

## 27.5 Strongly Connected Components (SCC)

### What It Finds

Groups where every node can reach every other node following direction.

### Implementation

```cypher
// Project directed graph
CALL gds.graph.project('directedNetwork', 'Page', 'LINKS_TO')

// Find SCCs
CALL gds.scc.stream('directedNetwork')
YIELD nodeId, componentId
RETURN componentId, count(*) AS size
ORDER BY size DESC

// Write results
CALL gds.scc.write('directedNetwork', {
    writeProperty: 'sccId'
})
YIELD componentCount, nodePropertiesWritten
```

---

## 27.6 Triangle Count and Clustering

### Triangle Count

Count triangles each node participates in:

```cypher
CALL gds.triangleCount.stream('socialNetwork')
YIELD nodeId, triangleCount
RETURN gds.util.asNode(nodeId).name AS person, triangleCount
ORDER BY triangleCount DESC

// Total triangles in graph
CALL gds.triangleCount.stats('socialNetwork')
YIELD globalTriangleCount, nodeCount
RETURN globalTriangleCount
```

### Local Clustering Coefficient

Density of a node's neighborhood:

```cypher
CALL gds.localClusteringCoefficient.stream('socialNetwork')
YIELD nodeId, localClusteringCoefficient
RETURN gds.util.asNode(nodeId).name AS person, 
       localClusteringCoefficient AS clustering
ORDER BY clustering DESC

// Average clustering coefficient
CALL gds.localClusteringCoefficient.stats('socialNetwork')
YIELD averageClusteringCoefficient
RETURN averageClusteringCoefficient
```

### Pre-computed Triangles

For efficiency with clustering coefficient:

```cypher
// First compute triangle counts
CALL gds.triangleCount.mutate('socialNetwork', {
    mutateProperty: 'triangleCount'
})

// Then use for clustering coefficient
CALL gds.localClusteringCoefficient.stream('socialNetwork', {
    triangleCountProperty: 'triangleCount'
})
YIELD nodeId, localClusteringCoefficient
RETURN gds.util.asNode(nodeId).name, localClusteringCoefficient
```

---

## 27.7 K-1 Coloring

### What It Does

Assigns colors so no adjacent nodes have the same color (approximately).

```cypher
CALL gds.k1coloring.stream('socialNetwork', {
    maxIterations: 10
})
YIELD nodeId, color
RETURN color, count(*) AS nodesWithColor
ORDER BY nodesWithColor DESC

// Write colors
CALL gds.k1coloring.write('socialNetwork', {
    writeProperty: 'color',
    maxIterations: 20
})
YIELD colorCount, ranIterations, didConverge
```

### Use Cases

- Task scheduling (non-conflicting assignments)
- Register allocation
- Graph partitioning

---

## 27.8 Leiden Algorithm

### Improvement Over Louvain

Leiden guarantees well-connected communities and avoids poorly connected ones.

```cypher
// Leiden community detection
CALL gds.leiden.stream('socialNetwork', {
    maxLevels: 10,
    includeIntermediateCommunities: true
})
YIELD nodeId, communityId, intermediateCommunityIds
RETURN gds.util.asNode(nodeId).name AS name,
       communityId,
       intermediateCommunityIds
ORDER BY communityId

// Statistics
CALL gds.leiden.stats('socialNetwork')
YIELD communityCount, modularity, ranLevels
RETURN *

// Write results
CALL gds.leiden.write('socialNetwork', {
    writeProperty: 'leidenCommunity'
})
YIELD communityCount, modularity
```

---

## 27.9 Community Quality Metrics

### Modularity

```cypher
// Get modularity from Louvain
CALL gds.louvain.stats('socialNetwork')
YIELD modularity
RETURN modularity
```

### Conductance

Measure how well-separated communities are:

```cypher
// Calculate conductance for each community
MATCH (n:Person)
WHERE n.community IS NOT NULL
WITH n.community AS community, collect(n) AS members
MATCH (m1:Person)-[r:KNOWS]-(m2:Person)
WHERE m1 IN members
WITH community, members,
     sum(CASE WHEN m2 IN members THEN 1 ELSE 0 END) AS internal,
     sum(CASE WHEN NOT m2 IN members THEN 1 ELSE 0 END) AS external
RETURN community,
       size(members) AS size,
       internal AS internalEdges,
       external AS boundaryEdges,
       toFloat(external) / (internal + external) AS conductance
ORDER BY conductance
```

### Coverage

Fraction of edges within communities:

```cypher
// Total internal vs external edges
MATCH (n1:Person)-[:KNOWS]-(n2:Person)
WHERE n1.community IS NOT NULL AND n2.community IS NOT NULL
WITH n1.community = n2.community AS internal, count(*) AS edges
RETURN internal, edges
```

---

## 27.10 Python Integration

```python
from neo4j import GraphDatabase
from typing import List, Dict
import pandas as pd

URI = "neo4j://localhost:7687"
AUTH = ("neo4j", "password")

class CommunityDetector:
    def __init__(self, uri, auth):
        self.driver = GraphDatabase.driver(uri, auth=auth)
    
    def close(self):
        self.driver.close()
    
    def project_graph(self, name: str, label: str, rel_type: str,
                      weight_property: str = None):
        """Project graph for community detection."""
        with self.driver.session() as session:
            session.run("CALL gds.graph.drop($name, false)", name=name)
            
            if weight_property:
                rel_config = f"{{type: '{rel_type}', properties: '{weight_property}'}}"
                query = f"""
                    CALL gds.graph.project(
                        $name, $label, {rel_config}
                    )
                    YIELD nodeCount, relationshipCount
                    RETURN nodeCount, relationshipCount
                """
            else:
                query = """
                    CALL gds.graph.project($name, $label, $relType)
                    YIELD nodeCount, relationshipCount
                    RETURN nodeCount, relationshipCount
                """
            
            result = session.run(query, name=name, label=label, relType=rel_type)
            return dict(result.single())
    
    def detect_louvain(self, graph_name: str, 
                       include_hierarchy: bool = False) -> List[Dict]:
        """Run Louvain community detection."""
        with self.driver.session() as session:
            if include_hierarchy:
                result = session.run("""
                    CALL gds.louvain.stream($graph, {
                        includeIntermediateCommunities: true
                    })
                    YIELD nodeId, communityId, intermediateCommunityIds
                    RETURN gds.util.asNode(nodeId).name AS name,
                           communityId AS community,
                           intermediateCommunityIds AS hierarchy
                """, graph=graph_name)
            else:
                result = session.run("""
                    CALL gds.louvain.stream($graph)
                    YIELD nodeId, communityId
                    RETURN gds.util.asNode(nodeId).name AS name,
                           communityId AS community
                """, graph=graph_name)
            
            return [dict(r) for r in result]
    
    def detect_label_propagation(self, graph_name: str,
                                  max_iterations: int = 10) -> List[Dict]:
        """Run Label Propagation."""
        with self.driver.session() as session:
            result = session.run("""
                CALL gds.labelPropagation.stream($graph, {
                    maxIterations: $maxIter
                })
                YIELD nodeId, communityId
                RETURN gds.util.asNode(nodeId).name AS name,
                       communityId AS community
            """, graph=graph_name, maxIter=max_iterations)
            
            return [dict(r) for r in result]
    
    def find_components(self, graph_name: str, 
                        strongly_connected: bool = False) -> List[Dict]:
        """Find connected components."""
        with self.driver.session() as session:
            algo = "gds.scc" if strongly_connected else "gds.wcc"
            result = session.run(f"""
                CALL {algo}.stream($graph)
                YIELD nodeId, componentId
                RETURN componentId AS component,
                       count(*) AS size,
                       collect(gds.util.asNode(nodeId).name) AS members
                ORDER BY size DESC
            """, graph=graph_name)
            
            return [dict(r) for r in result]
    
    def get_community_stats(self, graph_name: str) -> Dict:
        """Get community statistics from Louvain."""
        with self.driver.session() as session:
            result = session.run("""
                CALL gds.louvain.stats($graph)
                YIELD communityCount, modularity, ranLevels, 
                      communityDistribution, preProcessingMillis, computeMillis
                RETURN *
            """, graph=graph_name)
            
            return dict(result.single())
    
    def compare_algorithms(self, graph_name: str) -> pd.DataFrame:
        """Compare community detection algorithms."""
        louvain = self.detect_louvain(graph_name)
        lp = self.detect_label_propagation(graph_name)
        
        # Create comparison DataFrame
        data = {r['name']: {'louvain': r['community']} for r in louvain}
        for r in lp:
            if r['name'] in data:
                data[r['name']]['labelProp'] = r['community']
        
        df = pd.DataFrame.from_dict(data, orient='index')
        df.index.name = 'name'
        df.reset_index(inplace=True)
        
        # Check agreement
        df['agree'] = df['louvain'] == df['labelProp']
        
        return df
    
    def write_communities(self, graph_name: str, property_name: str,
                          algorithm: str = 'louvain') -> Dict:
        """Write community assignments to database."""
        with self.driver.session() as session:
            algo_map = {
                'louvain': 'gds.louvain.write',
                'labelPropagation': 'gds.labelPropagation.write',
                'wcc': 'gds.wcc.write',
                'leiden': 'gds.leiden.write'
            }
            
            algo = algo_map.get(algorithm, 'gds.louvain.write')
            result = session.run(f"""
                CALL {algo}($graph, {{writeProperty: $prop}})
                YIELD nodePropertiesWritten, communityCount
                RETURN nodePropertiesWritten, communityCount
            """, graph=graph_name, prop=property_name)
            
            return dict(result.single())
    
    def get_community_summary(self, graph_name: str) -> List[Dict]:
        """Get summary of detected communities."""
        communities = self.detect_louvain(graph_name)
        
        # Group by community
        from collections import defaultdict
        comm_groups = defaultdict(list)
        for r in communities:
            comm_groups[r['community']].append(r['name'])
        
        summary = []
        for comm_id, members in comm_groups.items():
            summary.append({
                'community': comm_id,
                'size': len(members),
                'members': members[:10],  # First 10 members
                'sample_members': ', '.join(members[:5])
            })
        
        return sorted(summary, key=lambda x: x['size'], reverse=True)

# Usage
detector = CommunityDetector(URI, AUTH)
try:
    # Project graph
    stats = detector.project_graph('social', 'Person', 'KNOWS')
    print(f"Projected: {stats['nodeCount']} nodes, {stats['relationshipCount']} relationships")
    
    # Get community statistics
    comm_stats = detector.get_community_stats('social')
    print(f"\nCommunity Statistics:")
    print(f"  Communities: {comm_stats['communityCount']}")
    print(f"  Modularity: {comm_stats['modularity']:.4f}")
    print(f"  Hierarchy Levels: {comm_stats['ranLevels']}")
    
    # Get community summary
    summary = detector.get_community_summary('social')
    print(f"\nCommunity Summary:")
    for s in summary[:5]:
        print(f"  Community {s['community']}: {s['size']} members - {s['sample_members']}")
    
    # Compare algorithms
    comparison = detector.compare_algorithms('social')
    agreement = comparison['agree'].mean() * 100
    print(f"\nAlgorithm Agreement: {agreement:.1f}%")
    
    # Find connected components
    components = detector.find_components('social')
    print(f"\nConnected Components: {len(components)}")
    for c in components[:3]:
        print(f"  Component {c['component']}: {c['size']} members")
    
finally:
    detector.close()
```

---

## Summary

### Algorithm Comparison

| Algorithm | Speed | Quality | Deterministic | Hierarchical |
|-----------|-------|---------|---------------|--------------|
| Louvain | Medium | High | Yes | Yes |
| Label Propagation | Fast | Medium | No | No |
| WCC | Fast | N/A | Yes | No |
| Leiden | Medium | Very High | Yes | Yes |
| Triangle Count | Medium | N/A | Yes | No |

### When to Use What

| Scenario | Recommended Algorithm |
|----------|----------------------|
| General community detection | Louvain or Leiden |
| Very large graphs | Label Propagation |
| Finding disconnected groups | WCC |
| Directed graphs | SCC |
| Quality over speed | Leiden |
| Reproducible results | Louvain or Leiden (with seed) |

---

## Exercises

### Exercise 27.1: Community Analysis
1. Load a social network dataset
2. Run Louvain community detection
3. Analyze community sizes and characteristics

### Exercise 27.2: Algorithm Comparison
1. Run Louvain, Label Propagation, and Leiden on the same graph
2. Compare results and measure agreement
3. Evaluate which produces better communities

### Exercise 27.3: Hierarchical Communities
1. Use Louvain with intermediate communities
2. Visualize the hierarchy
3. Find natural community granularity levels

---

**Next Chapter: [Chapter 28: Similarity Algorithms](28-similarity-algorithms.md)**
