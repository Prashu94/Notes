"""
Centrality Algorithms for Energy Grid
Identify important nodes in the power grid network.
"""

from typing import List, Dict, Any
from neo4j import Driver


class CentralityAlgorithms:
    """Centrality algorithms using Neo4j GDS."""
    
    def __init__(self, driver: Driver):
        """Initialize with Neo4j driver."""
        self.driver = driver
    
    def degree_centrality(self, node_type: str = "Substation", top_k: int = 10) -> List[Dict[str, Any]]:
        """Calculate degree centrality to find most connected nodes."""
        with self.driver.session() as session:
            query = f"""
            MATCH (n:{node_type})
            OPTIONAL MATCH (n)-[r:CONNECTED_TO]-()
            WITH n, count(r) as degree
            ORDER BY degree DESC
            LIMIT $top_k
            OPTIONAL MATCH (n)-[:LOCATED_IN]->(l:Location)
            RETURN 
                n.id as node_id,
                n.name as node_name,
                n.type as node_type,
                n.status as status,
                l.name as location,
                degree,
                degree * 1.0 / (SELECT count(*) FROM (MATCH (:{node_type}) RETURN 1)) as normalized_degree
            """
            
            result = session.run(query, top_k=top_k)
            return [dict(record) for record in result]
    
    def betweenness_centrality(
        self,
        node_type: str = "Substation",
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """Calculate betweenness centrality to find bridge nodes."""
        with self.driver.session() as session:
            # First create projection
            projection_name = f"betweenness_projection_{node_type}"
            
            create_projection = """
            CALL gds.graph.project(
                $projection_name,
                $node_type,
                'CONNECTED_TO',
                {relationshipProperties: 'distance_km'}
            )
            YIELD graphName, nodeCount, relationshipCount
            RETURN graphName, nodeCount, relationshipCount
            """
            
            try:
                # Drop existing projection if exists
                session.run(f"CALL gds.graph.drop('{projection_name}', false)")
            except:
                pass
            
            # Create new projection
            session.run(
                create_projection,
                projection_name=projection_name,
                node_type=node_type
            )
            
            # Run betweenness centrality
            query = """
            CALL gds.betweenness.stream($projection_name)
            YIELD nodeId, score
            WITH gds.util.asNode(nodeId) AS node, score
            ORDER BY score DESC
            LIMIT $top_k
            OPTIONAL MATCH (node)-[:LOCATED_IN]->(l:Location)
            RETURN 
                node.id as node_id,
                node.name as node_name,
                node.type as node_type,
                node.status as status,
                l.name as location,
                score as betweenness_score
            """
            
            result = session.run(query, projection_name=projection_name, top_k=top_k)
            nodes = [dict(record) for record in result]
            
            # Clean up
            session.run(f"CALL gds.graph.drop('{projection_name}')")
            
            return nodes
    
    def pagerank(
        self,
        node_type: str = "Substation",
        top_k: int = 10,
        damping_factor: float = 0.85
    ) -> List[Dict[str, Any]]:
        """Calculate PageRank to find influential nodes."""
        with self.driver.session() as session:
            projection_name = f"pagerank_projection_{node_type}"
            
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
            
            # Run PageRank
            query = """
            CALL gds.pageRank.stream($projection_name, {
                dampingFactor: $damping_factor
            })
            YIELD nodeId, score
            WITH gds.util.asNode(nodeId) AS node, score
            ORDER BY score DESC
            LIMIT $top_k
            OPTIONAL MATCH (node)-[:LOCATED_IN]->(l:Location)
            OPTIONAL MATCH (node)-[:SUPPLIES_TO]->(c:Customer)
            WITH node, l, score, count(c) as customer_count, sum(c.consumption_mw) as total_load
            RETURN 
                node.id as node_id,
                node.name as node_name,
                node.type as node_type,
                node.status as status,
                l.name as location,
                score as pagerank_score,
                customer_count,
                total_load
            """
            
            result = session.run(
                query,
                projection_name=projection_name,
                top_k=top_k,
                damping_factor=damping_factor
            )
            nodes = [dict(record) for record in result]
            
            # Clean up
            session.run(f"CALL gds.graph.drop('{projection_name}')")
            
            return nodes
    
    def closeness_centrality(
        self,
        node_type: str = "Substation",
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """Calculate closeness centrality to find well-connected nodes."""
        with self.driver.session() as session:
            projection_name = f"closeness_projection_{node_type}"
            
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
            
            # Run closeness centrality
            query = """
            CALL gds.closeness.stream($projection_name)
            YIELD nodeId, score
            WITH gds.util.asNode(nodeId) AS node, score
            ORDER BY score DESC
            LIMIT $top_k
            OPTIONAL MATCH (node)-[:LOCATED_IN]->(l:Location)
            RETURN 
                node.id as node_id,
                node.name as node_name,
                node.type as node_type,
                node.status as status,
                l.name as location,
                score as closeness_score
            """
            
            result = session.run(query, projection_name=projection_name, top_k=top_k)
            nodes = [dict(record) for record in result]
            
            # Clean up
            session.run(f"CALL gds.graph.drop('{projection_name}')")
            
            return nodes
    
    def identify_critical_nodes(self, top_k: int = 10) -> List[Dict[str, Any]]:
        """Identify critical nodes using multiple centrality measures."""
        with self.driver.session() as session:
            # Get degree centrality
            degree = self.degree_centrality("Substation", top_k=50)
            
            # Get betweenness
            betweenness = self.betweenness_centrality("Substation", top_k=50)
            
            # Get PageRank
            pagerank = self.pagerank("Substation", top_k=50)
            
            # Combine scores
            combined_scores = {}
            
            for node in degree:
                node_id = node["node_id"]
                combined_scores[node_id] = {
                    "node_id": node_id,
                    "node_name": node["node_name"],
                    "location": node["location"],
                    "degree": node["degree"],
                    "betweenness": 0,
                    "pagerank": 0
                }
            
            for node in betweenness:
                node_id = node["node_id"]
                if node_id in combined_scores:
                    combined_scores[node_id]["betweenness"] = node["betweenness_score"]
            
            for node in pagerank:
                node_id = node["node_id"]
                if node_id in combined_scores:
                    combined_scores[node_id]["pagerank"] = node["pagerank_score"]
            
            # Calculate combined criticality score (normalized)
            for node_id in combined_scores:
                node = combined_scores[node_id]
                # Simple average of normalized scores
                node["criticality_score"] = (
                    (node["degree"] / max(n["degree"] for n in combined_scores.values()) * 0.4) +
                    (node["betweenness"] / max(n["betweenness"] for n in combined_scores.values()) * 0.4 if node["betweenness"] > 0 else 0) +
                    (node["pagerank"] / max(n["pagerank"] for n in combined_scores.values()) * 0.2 if node["pagerank"] > 0 else 0)
                )
            
            # Sort by criticality
            result = sorted(
                combined_scores.values(),
                key=lambda x: x["criticality_score"],
                reverse=True
            )[:top_k]
            
            return result
    
    def analyze_node_importance(self, node_id: str) -> Dict[str, Any]:
        """Analyze a single node's importance in the network."""
        with self.driver.session() as session:
            query = """
            MATCH (n {id: $node_id})
            OPTIONAL MATCH (n)-[r:CONNECTED_TO]-(connected)
            WITH n, count(r) as degree, collect(connected.name) as connected_nodes
            
            OPTIONAL MATCH (n)-[:SUPPLIES_TO]->(c:Customer)
            WITH n, degree, connected_nodes, count(c) as customer_count, sum(c.consumption_mw) as total_load
            
            OPTIONAL MATCH path = shortestPath((n)-[:CONNECTED_TO*]-(other:Substation))
            WHERE n <> other
            WITH n, degree, connected_nodes, customer_count, total_load,
                 avg(length(path)) as avg_distance_to_others
            
            OPTIONAL MATCH (n)-[:LOCATED_IN]->(l:Location)
            
            RETURN 
                n.id as node_id,
                n.name as node_name,
                labels(n)[0] as node_type,
                n.status as status,
                l.name as location,
                degree,
                connected_nodes,
                customer_count,
                total_load,
                avg_distance_to_others,
                CASE 
                    WHEN degree >= 4 AND customer_count > 2 THEN 'CRITICAL'
                    WHEN degree >= 3 OR customer_count > 1 THEN 'HIGH'
                    WHEN degree >= 2 THEN 'MEDIUM'
                    ELSE 'LOW'
                END as importance_level
            """
            
            result = session.run(query, node_id=node_id)
            record = result.single()
            return dict(record) if record else {}
