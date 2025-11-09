-- ============================================================================
-- Graph Algorithms for Energy Grid Analysis
-- ============================================================================
-- This file demonstrates graph algorithms using Neo4j GDS (Graph Data Science)
-- Prerequisites: Install Neo4j GDS plugin

-- ============================================================================
-- 1. PROJECT GRAPH (Create in-memory graph projection)
-- ============================================================================

-- Create graph projection for analysis
CALL gds.graph.project(
    'energyGrid',
    ['PowerPlant', 'Substation', 'Customer'],
    {
        GENERATES: {orientation: 'NATURAL'},
        TRANSMITS_TO: {
            orientation: 'UNDIRECTED',
            properties: ['capacity_mw', 'distance_km']
        },
        SUPPLIES_POWER: {orientation: 'NATURAL'}
    }
);

-- ============================================================================
-- 2. SHORTEST PATH ALGORITHMS
-- ============================================================================

-- Find shortest path between two substations (Dijkstra)
MATCH (source:Substation {id: 'SUB-001'})
MATCH (target:Substation {id: 'SUB-008'})
CALL gds.shortestPath.dijkstra.stream('energyGrid', {
    sourceNode: source,
    targetNode: target,
    relationshipWeightProperty: 'distance_km'
})
YIELD index, sourceNode, targetNode, totalCost, nodeIds, costs, path
RETURN
    index,
    gds.util.asNode(sourceNode).name AS sourceNodeName,
    gds.util.asNode(targetNode).name AS targetNodeName,
    totalCost,
    [nodeId IN nodeIds | gds.util.asNode(nodeId).name] AS nodeNames,
    costs,
    nodes(path) as path
ORDER BY index;

-- Find all shortest paths from a power plant
MATCH (source:PowerPlant {id: 'PLANT-001'})
CALL gds.allShortestPaths.dijkstra.stream('energyGrid', {
    sourceNode: source,
    relationshipWeightProperty: 'distance_km'
})
YIELD index, sourceNode, targetNode, totalCost, nodeIds
RETURN
    gds.util.asNode(sourceNode).name AS source,
    gds.util.asNode(targetNode).name AS target,
    totalCost AS distance_km,
    [nodeId IN nodeIds | gds.util.asNode(nodeId).name] AS path
ORDER BY totalCost
LIMIT 20;

-- ============================================================================
-- 3. CENTRALITY ALGORITHMS
-- ============================================================================

-- Degree Centrality (Find most connected substations)
CALL gds.degree.stream('energyGrid')
YIELD nodeId, score
WITH gds.util.asNode(nodeId) AS node, score
WHERE 'Substation' IN labels(node)
RETURN
    node.id AS substation_id,
    node.name AS substation_name,
    score AS connection_count
ORDER BY score DESC
LIMIT 10;

-- Betweenness Centrality (Find critical infrastructure)
CALL gds.betweenness.stream('energyGrid')
YIELD nodeId, score
WITH gds.util.asNode(nodeId) AS node, score
WHERE score > 0
RETURN
    labels(node)[0] AS node_type,
    node.id AS node_id,
    node.name AS node_name,
    score AS betweenness_centrality
ORDER BY score DESC
LIMIT 15;

-- PageRank (Identify important nodes in power flow)
CALL gds.pageRank.stream('energyGrid')
YIELD nodeId, score
WITH gds.util.asNode(nodeId) AS node, score
RETURN
    labels(node)[0] AS node_type,
    node.id AS node_id,
    node.name AS node_name,
    score AS pagerank_score
ORDER BY score DESC
LIMIT 15;

-- Closeness Centrality (Find well-connected substations)
CALL gds.closeness.stream('energyGrid')
YIELD nodeId, score
WITH gds.util.asNode(nodeId) AS node, score
WHERE 'Substation' IN labels(node) AND score > 0
RETURN
    node.id AS substation_id,
    node.name AS substation_name,
    score AS closeness_score
ORDER BY score DESC
LIMIT 10;

-- ============================================================================
-- 4. COMMUNITY DETECTION
-- ============================================================================

-- Louvain Community Detection (Find grid regions/clusters)
CALL gds.louvain.stream('energyGrid')
YIELD nodeId, communityId, intermediateCommunityIds
WITH gds.util.asNode(nodeId) AS node, communityId
RETURN
    communityId,
    collect(DISTINCT labels(node)[0]) AS node_types,
    count(*) AS member_count,
    collect(node.name)[0..5] AS sample_members
ORDER BY member_count DESC;

-- Label Propagation (Alternative community detection)
CALL gds.labelPropagation.stream('energyGrid')
YIELD nodeId, communityId
WITH gds.util.asNode(nodeId) AS node, communityId
WHERE 'Substation' IN labels(node)
RETURN
    communityId,
    count(*) AS substation_count,
    collect(node.name) AS substations
ORDER BY substation_count DESC;

-- ============================================================================
-- 5. SIMILARITY ALGORITHMS
-- ============================================================================

-- Node Similarity (Find similar substations based on connections)
CALL gds.nodeSimilarity.stream('energyGrid')
YIELD node1, node2, similarity
WITH gds.util.asNode(node1) AS n1, gds.util.asNode(node2) AS n2, similarity
WHERE 'Substation' IN labels(n1) AND 'Substation' IN labels(n2)
RETURN
    n1.name AS substation1,
    n2.name AS substation2,
    similarity
ORDER BY similarity DESC
LIMIT 20;

-- ============================================================================
-- 6. PATH FINDING
-- ============================================================================

-- K-Shortest Paths (Find alternative routes)
MATCH (source:Substation {id: 'SUB-001'})
MATCH (target:Substation {id: 'SUB-008'})
CALL gds.shortestPath.yens.stream('energyGrid', {
    sourceNode: source,
    targetNode: target,
    k: 5,
    relationshipWeightProperty: 'distance_km'
})
YIELD index, sourceNode, targetNode, totalCost, nodeIds, costs
RETURN
    index AS path_number,
    totalCost AS total_distance_km,
    [nodeId IN nodeIds | gds.util.asNode(nodeId).name] AS route,
    costs
ORDER BY index;

-- All Pairs Shortest Path (expensive - use with caution)
CALL gds.allShortestPaths.dijkstra.stream('energyGrid', {
    relationshipWeightProperty: 'distance_km'
})
YIELD sourceNode, targetNode, totalCost
WITH gds.util.asNode(sourceNode) AS source, gds.util.asNode(targetNode) AS target, totalCost
WHERE 'Substation' IN labels(source) AND 'Substation' IN labels(target)
RETURN
    source.name AS from_substation,
    target.name AS to_substation,
    totalCost AS distance_km
ORDER BY totalCost DESC
LIMIT 20;

-- ============================================================================
-- 7. NETWORK ANALYSIS
-- ============================================================================

-- Triangle Count (Find tightly connected components)
CALL gds.triangleCount.stream('energyGrid')
YIELD nodeId, triangleCount
WITH gds.util.asNode(nodeId) AS node, triangleCount
WHERE triangleCount > 0
RETURN
    labels(node)[0] AS node_type,
    node.name AS node_name,
    triangleCount
ORDER BY triangleCount DESC
LIMIT 10;

-- Local Clustering Coefficient
CALL gds.localClusteringCoefficient.stream('energyGrid')
YIELD nodeId, localClusteringCoefficient
WITH gds.util.asNode(nodeId) AS node, localClusteringCoefficient
WHERE localClusteringCoefficient > 0
RETURN
    node.name AS node_name,
    localClusteringCoefficient AS clustering_coefficient
ORDER BY localClusteringCoefficient DESC
LIMIT 10;

-- ============================================================================
-- 8. WEAKLY CONNECTED COMPONENTS
-- ============================================================================

-- Find disconnected parts of the grid
CALL gds.wcc.stream('energyGrid')
YIELD nodeId, componentId
WITH componentId, collect(gds.util.asNode(nodeId).name) AS members
RETURN
    componentId,
    size(members) AS component_size,
    members
ORDER BY component_size DESC;

-- ============================================================================
-- 9. STRONGLY CONNECTED COMPONENTS
-- ============================================================================

-- Find strongly connected regions (considering direction)
CALL gds.alpha.scc.stream('energyGrid')
YIELD nodeId, componentId
WITH componentId, collect(gds.util.asNode(nodeId).name) AS members
WHERE size(members) > 1
RETURN
    componentId,
    size(members) AS component_size,
    members
ORDER BY component_size DESC;

-- ============================================================================
-- 10. CLEANUP
-- ============================================================================

-- Drop graph projection when done
CALL gds.graph.drop('energyGrid', false);

-- List all graph projections
CALL gds.graph.list();
