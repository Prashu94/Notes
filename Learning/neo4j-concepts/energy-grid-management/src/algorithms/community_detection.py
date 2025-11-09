"""
Community Detection Algorithms for Energy Grid
Identify clusters and communities in the power grid.
"""

from typing import List, Dict, Any
from neo4j import Driver


class CommunityDetectionAlgorithms:
    """Community detection algorithms using Neo4j GDS."""
    
    def __init__(self, driver: Driver):
        """Initialize with Neo4j driver."""
        self.driver = driver
    
    def louvain_communities(
        self,
        node_type: str = "Substation",
        relationship_type: str = "CONNECTED_TO"
    ) -> List[Dict[str, Any]]:
        """Detect communities using Louvain algorithm."""
        with self.driver.session() as session:
            projection_name = "louvain_projection"
            
            try:
                session.run(f"CALL gds.graph.drop('{projection_name}', false)")
            except:
                pass
            
            # Create projection
            session.run(
                """
                CALL gds.graph.project(
                    $projection_name,
                    $node_type,
                    $relationship_type
                )
                """,
                projection_name=projection_name,
                node_type=node_type,
                relationship_type=relationship_type
            )
            
            # Run Louvain
            query = """
            CALL gds.louvain.stream($projection_name)
            YIELD nodeId, communityId
            WITH gds.util.asNode(nodeId) AS node, communityId
            OPTIONAL MATCH (node)-[:LOCATED_IN]->(l:Location)
            RETURN 
                communityId,
                collect({
                    node_id: node.id,
                    node_name: node.name,
                    node_type: labels(node)[0],
                    location: l.name
                }) as members,
                count(node) as community_size
            ORDER BY community_size DESC
            """
            
            result = session.run(query, projection_name=projection_name)
            communities = [dict(record) for record in result]
            
            # Clean up
            session.run(f"CALL gds.graph.drop('{projection_name}')")
            
            return communities
    
    def label_propagation(
        self,
        node_type: str = "Substation",
        max_iterations: int = 10
    ) -> List[Dict[str, Any]]:
        """Detect communities using Label Propagation algorithm."""
        with self.driver.session() as session:
            projection_name = "label_prop_projection"
            
            try:
                session.run(f"CALL gds.graph.drop('{projection_name}', false)")
            except:
                pass
            
            # Create projection
            session.run(
                """
                CALL gds.graph.project(
                    $projection_name,
                    $node_type,
                    'CONNECTED_TO'
                )
                """,
                projection_name=projection_name,
                node_type=node_type
            )
            
            # Run Label Propagation
            query = """
            CALL gds.labelPropagation.stream($projection_name, {
                maxIterations: $max_iterations
            })
            YIELD nodeId, communityId
            WITH gds.util.asNode(nodeId) AS node, communityId
            OPTIONAL MATCH (node)-[:LOCATED_IN]->(l:Location)
            RETURN 
                communityId,
                collect({
                    node_id: node.id,
                    node_name: node.name,
                    location: l.name
                }) as members,
                count(node) as community_size
            ORDER BY community_size DESC
            """
            
            result = session.run(
                query,
                projection_name=projection_name,
                max_iterations=max_iterations
            )
            communities = [dict(record) for record in result]
            
            # Clean up
            session.run(f"CALL gds.graph.drop('{projection_name}')")
            
            return communities
    
    def weakly_connected_components(self) -> List[Dict[str, Any]]:
        """Find weakly connected components (isolated networks)."""
        with self.driver.session() as session:
            projection_name = "wcc_projection"
            
            try:
                session.run(f"CALL gds.graph.drop('{projection_name}', false)")
            except:
                pass
            
            # Create projection
            session.run(
                """
                CALL gds.graph.project(
                    $projection_name,
                    ['Substation', 'PowerPlant'],
                    'CONNECTED_TO'
                )
                """,
                projection_name=projection_name
            )
            
            # Run WCC
            query = """
            CALL gds.wcc.stream($projection_name)
            YIELD nodeId, componentId
            WITH gds.util.asNode(nodeId) AS node, componentId
            OPTIONAL MATCH (node)-[:LOCATED_IN]->(l:Location)
            RETURN 
                componentId,
                collect({
                    node_id: node.id,
                    node_name: node.name,
                    node_type: labels(node)[0],
                    location: l.name
                }) as members,
                count(node) as component_size
            ORDER BY component_size DESC
            """
            
            result = session.run(query, projection_name=projection_name)
            components = [dict(record) for record in result]
            
            # Clean up
            session.run(f"CALL gds.graph.drop('{projection_name}')")
            
            return components
    
    def triangle_count_clustering(
        self,
        node_type: str = "Substation"
    ) -> List[Dict[str, Any]]:
        """Calculate triangle count and clustering coefficient."""
        with self.driver.session() as session:
            projection_name = "triangle_projection"
            
            try:
                session.run(f"CALL gds.graph.drop('{projection_name}', false)")
            except:
                pass
            
            # Create projection
            session.run(
                """
                CALL gds.graph.project(
                    $projection_name,
                    $node_type,
                    {
                        CONNECTED_TO: {
                            orientation: 'UNDIRECTED'
                        }
                    }
                )
                """,
                projection_name=projection_name,
                node_type=node_type
            )
            
            # Run triangle count
            query = """
            CALL gds.triangleCount.stream($projection_name)
            YIELD nodeId, triangleCount
            WITH gds.util.asNode(nodeId) AS node, triangleCount
            WHERE triangleCount > 0
            OPTIONAL MATCH (node)-[:CONNECTED_TO]-(connected)
            WITH node, triangleCount, count(DISTINCT connected) as degree
            OPTIONAL MATCH (node)-[:LOCATED_IN]->(l:Location)
            RETURN 
                node.id as node_id,
                node.name as node_name,
                l.name as location,
                triangleCount,
                degree,
                CASE 
                    WHEN degree > 1 THEN (2.0 * triangleCount / (degree * (degree - 1)))
                    ELSE 0
                END as clustering_coefficient
            ORDER BY triangleCount DESC
            LIMIT 20
            """
            
            result = session.run(query, projection_name=projection_name)
            nodes = [dict(record) for record in result]
            
            # Clean up
            session.run(f"CALL gds.graph.drop('{projection_name}')")
            
            return nodes
    
    def node_similarity(
        self,
        node_type: str = "Substation",
        top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """Find similar nodes based on connectivity patterns."""
        with self.driver.session() as session:
            projection_name = "similarity_projection"
            
            try:
                session.run(f"CALL gds.graph.drop('{projection_name}', false)")
            except:
                pass
            
            # Create projection
            session.run(
                """
                CALL gds.graph.project(
                    $projection_name,
                    $node_type,
                    'CONNECTED_TO'
                )
                """,
                projection_name=projection_name,
                node_type=node_type
            )
            
            # Run node similarity
            query = """
            CALL gds.nodeSimilarity.stream($projection_name, {
                topK: $top_k
            })
            YIELD node1, node2, similarity
            WITH gds.util.asNode(node1) AS n1, gds.util.asNode(node2) AS n2, similarity
            OPTIONAL MATCH (n1)-[:LOCATED_IN]->(l1:Location)
            OPTIONAL MATCH (n2)-[:LOCATED_IN]->(l2:Location)
            RETURN 
                n1.id as node1_id,
                n1.name as node1_name,
                l1.name as node1_location,
                n2.id as node2_id,
                n2.name as node2_name,
                l2.name as node2_location,
                similarity
            ORDER BY similarity DESC
            LIMIT 50
            """
            
            result = session.run(query, projection_name=projection_name, top_k=top_k)
            pairs = [dict(record) for record in result]
            
            # Clean up
            session.run(f"CALL gds.graph.drop('{projection_name}')")
            
            return pairs
    
    def identify_regional_clusters(self) -> Dict[str, Any]:
        """Identify regional clusters and analyze their properties."""
        with self.driver.session() as session:
            # Get communities
            communities = self.louvain_communities()
            
            # Analyze each community
            community_analysis = []
            
            for i, community in enumerate(communities):
                members = community["members"]
                member_ids = [m["node_id"] for m in members]
                
                # Get community properties
                analysis_query = """
                MATCH (n)
                WHERE n.id IN $member_ids
                OPTIONAL MATCH (n)-[:CONNECTED_TO]-(internal)
                WHERE internal.id IN $member_ids
                WITH n, count(DISTINCT internal) as internal_connections
                
                OPTIONAL MATCH (n)-[:CONNECTED_TO]-(external)
                WHERE NOT external.id IN $member_ids
                WITH n, internal_connections, count(DISTINCT external) as external_connections
                
                OPTIONAL MATCH (n)-[:SUPPLIES_TO]->(c:Customer)
                WITH n, internal_connections, external_connections, 
                     count(c) as customers, sum(c.consumption_mw) as total_load
                
                RETURN 
                    sum(internal_connections) / 2 as total_internal_edges,
                    sum(external_connections) as total_external_edges,
                    sum(customers) as total_customers,
                    sum(total_load) as total_load_mw,
                    collect(DISTINCT n.location) as locations
                """
                
                result = session.run(analysis_query, member_ids=member_ids)
                record = result.single()
                
                if record:
                    community_analysis.append({
                        "community_id": i + 1,
                        "size": community["community_size"],
                        "members": members,
                        **dict(record)
                    })
            
            return {
                "total_communities": len(communities),
                "communities": community_analysis
            }
