"""
Shortest Path Algorithms for Energy Grid
Wrappers for Neo4j GDS shortest path algorithms.
"""

from typing import List, Dict, Any, Optional
from neo4j import Driver


class ShortestPathAlgorithms:
    """Shortest path algorithms using Neo4j GDS."""
    
    def __init__(self, driver: Driver):
        """Initialize with Neo4j driver."""
        self.driver = driver
    
    def dijkstra_shortest_path(
        self,
        source_id: str,
        target_id: str,
        relationship_type: str = "CONNECTED_TO",
        weight_property: str = "distance_km"
    ) -> Dict[str, Any]:
        """Find shortest path using Dijkstra algorithm."""
        with self.driver.session() as session:
            query = """
            MATCH (source {id: $source_id}), (target {id: $target_id})
            CALL gds.shortestPath.dijkstra.stream({
                sourceNode: id(source),
                targetNode: id(target),
                relationshipWeightProperty: $weight_property
            })
            YIELD index, sourceNode, targetNode, totalCost, nodeIds, costs, path
            RETURN 
                [nodeId IN nodeIds | gds.util.asNode(nodeId).id] as node_ids,
                [nodeId IN nodeIds | gds.util.asNode(nodeId).name] as node_names,
                totalCost as total_cost,
                costs as segment_costs,
                size(nodeIds) - 1 as hop_count
            """
            
            result = session.run(
                query,
                source_id=source_id,
                target_id=target_id,
                weight_property=weight_property
            )
            record = result.single()
            return dict(record) if record else {}
    
    def yens_k_shortest_paths(
        self,
        source_id: str,
        target_id: str,
        k: int = 3,
        relationship_type: str = "CONNECTED_TO",
        weight_property: str = "distance_km"
    ) -> List[Dict[str, Any]]:
        """Find k shortest paths using Yen's algorithm."""
        with self.driver.session() as session:
            query = """
            MATCH (source {id: $source_id}), (target {id: $target_id})
            CALL gds.shortestPath.yens.stream({
                sourceNode: id(source),
                targetNode: id(target),
                k: $k,
                relationshipWeightProperty: $weight_property
            })
            YIELD index, sourceNode, targetNode, totalCost, nodeIds, costs, path
            RETURN 
                index as path_rank,
                [nodeId IN nodeIds | gds.util.asNode(nodeId).id] as node_ids,
                [nodeId IN nodeIds | gds.util.asNode(nodeId).name] as node_names,
                totalCost as total_cost,
                costs as segment_costs,
                size(nodeIds) - 1 as hop_count
            ORDER BY index
            """
            
            result = session.run(
                query,
                source_id=source_id,
                target_id=target_id,
                k=k,
                weight_property=weight_property
            )
            return [dict(record) for record in result]
    
    def all_shortest_paths(
        self,
        source_id: str,
        target_id: str,
        relationship_type: str = "CONNECTED_TO"
    ) -> List[Dict[str, Any]]:
        """Find all shortest paths between two nodes."""
        with self.driver.session() as session:
            query = """
            MATCH (source {id: $source_id}), (target {id: $target_id})
            MATCH paths = allShortestPaths((source)-[:CONNECTED_TO*]-(target))
            RETURN 
                [node IN nodes(paths) | node.id] as node_ids,
                [node IN nodes(paths) | node.name] as node_names,
                length(paths) as hop_count,
                [rel IN relationships(paths) | {
                    from: startNode(rel).name,
                    to: endNode(rel).name,
                    type: type(rel)
                }] as relationships
            """
            
            result = session.run(query, source_id=source_id, target_id=target_id)
            return [dict(record) for record in result]
    
    def find_power_flow_paths(
        self,
        plant_id: str,
        customer_id: str,
        max_hops: int = 5
    ) -> List[Dict[str, Any]]:
        """Find all possible power flow paths from plant to customer."""
        with self.driver.session() as session:
            query = """
            MATCH (plant:PowerPlant {id: $plant_id})
            MATCH (customer:Customer {id: $customer_id})
            MATCH path = (plant)-[:SUPPLIES_TO|CONNECTED_TO*1..$max_hops]->(customer)
            WHERE ALL(r IN relationships(path) WHERE r.status <> 'inactive')
            WITH path,
                 [node IN nodes(path) | node.name] as path_names,
                 length(path) as hop_count,
                 reduce(cap = 999999.0, rel IN relationships(path) | 
                     CASE 
                         WHEN 'capacity_mw' IN keys(startNode(rel)) 
                         THEN CASE WHEN startNode(rel).capacity_mw < cap 
                              THEN startNode(rel).capacity_mw 
                              ELSE cap END
                         ELSE cap
                     END
                 ) as bottleneck_capacity
            RETURN 
                path_names,
                hop_count,
                bottleneck_capacity,
                [node IN nodes(path) | {
                    id: node.id,
                    name: node.name,
                    type: labels(node)[0]
                }] as path_details
            ORDER BY hop_count, bottleneck_capacity DESC
            LIMIT 10
            """
            
            result = session.run(
                query,
                plant_id=plant_id,
                customer_id=customer_id,
                max_hops=max_hops
            )
            return [dict(record) for record in result]
    
    def find_alternative_routes(
        self,
        source_id: str,
        target_id: str,
        excluded_node_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Find alternative routes excluding a failed node."""
        with self.driver.session() as session:
            if excluded_node_id:
                query = """
                MATCH (source {id: $source_id}), (target {id: $target_id})
                MATCH (excluded {id: $excluded_id})
                MATCH path = shortestPath((source)-[:CONNECTED_TO*]-(target))
                WHERE NONE(node IN nodes(path) WHERE node = excluded)
                  AND ALL(r IN relationships(path) WHERE r.status <> 'inactive')
                RETURN 
                    [node IN nodes(path) | node.id] as node_ids,
                    [node IN nodes(path) | node.name] as node_names,
                    length(path) as hop_count
                """
                result = session.run(
                    query,
                    source_id=source_id,
                    target_id=target_id,
                    excluded_id=excluded_node_id
                )
            else:
                query = """
                MATCH (source {id: $source_id}), (target {id: $target_id})
                MATCH path = shortestPath((source)-[:CONNECTED_TO*]-(target))
                WHERE ALL(r IN relationships(path) WHERE r.status <> 'inactive')
                RETURN 
                    [node IN nodes(path) | node.id] as node_ids,
                    [node IN nodes(path) | node.name] as node_names,
                    length(path) as hop_count
                """
                result = session.run(query, source_id=source_id, target_id=target_id)
            
            return [dict(record) for record in result]
    
    def calculate_network_diameter(self) -> Dict[str, Any]:
        """Calculate network diameter (longest shortest path)."""
        with self.driver.session() as session:
            query = """
            MATCH (s:Substation), (t:Substation)
            WHERE s.id < t.id AND s.status = 'operational' AND t.status = 'operational'
            MATCH path = shortestPath((s)-[:CONNECTED_TO*]-(t))
            WITH length(path) as path_length, s, t
            RETURN 
                max(path_length) as diameter,
                avg(path_length) as average_path_length,
                min(path_length) as minimum_path_length,
                count(*) as total_paths_analyzed
            """
            
            result = session.run(query)
            record = result.single()
            return dict(record) if record else {}
