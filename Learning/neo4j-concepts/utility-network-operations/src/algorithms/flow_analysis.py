"""Flow analysis algorithms for network capacity and optimization."""

from typing import List, Dict, Any, Optional

from ..connection import Neo4jConnection


class FlowAnalysis:
    """Algorithms for analyzing flow capacity and distribution in utility networks."""
    
    def __init__(self):
        """Initialize with database connection."""
        self.conn = Neo4jConnection()
    
    def calculate_max_flow(
        self,
        source_id: str,
        sink_id: str,
        capacity_property: str = 'max_flow_rate'
    ) -> Dict[str, Any]:
        """
        Calculate maximum flow between source and sink.
        Uses Ford-Fulkerson algorithm concept.
        """
        query = """
        MATCH (source:StorageTank {id: $source_id})
        MATCH (sink:Customer {id: $sink_id})
        MATCH path = shortestPath((source)-[:SUPPLIES|CONNECTS_TO*]-(sink))
        WITH path, 
             [r IN relationships(path) | 
              coalesce(r.max_flow_rate, startNode(r).max_flow_rate, 1000.0)
             ] as capacities
        RETURN min([c IN capacities | c]) as bottleneck_capacity,
               length(path) as path_length,
               [n IN nodes(path) | n.id] as path_nodes
        """
        result = self.conn.execute_query(
            query,
            source_id=source_id,
            sink_id=sink_id
        )
        
        return result[0] if result else {}
    
    def identify_bottlenecks(
        self,
        min_capacity_threshold: float = 50.0
    ) -> List[Dict[str, Any]]:
        """Identify bottlenecks in the network (low capacity segments)."""
        query = """
        MATCH (p:PipelineSegment)
        WHERE p.max_flow_rate IS NOT NULL
          AND p.max_flow_rate < $threshold
        WITH p
        OPTIONAL MATCH (p)-[:CONNECTS_TO]-(neighbor:PipelineSegment)
        WHERE neighbor.max_flow_rate > $threshold * 1.5
        RETURN p.id as pipeline_id,
               p.max_flow_rate as capacity,
               p.diameter_mm as diameter,
               p.location as location,
               count(neighbor) as high_capacity_neighbors,
               CASE WHEN count(neighbor) > 0 THEN true ELSE false END as is_bottleneck
        ORDER BY capacity ASC, high_capacity_neighbors DESC
        """
        result = self.conn.execute_query(query, threshold=min_capacity_threshold)
        return result
    
    def analyze_network_capacity(
        self,
        region: Optional[str] = None
    ) -> Dict[str, Any]:
        """Analyze overall network capacity and utilization."""
        if region:
            query = """
            MATCH (p:PipelineSegment {region: $region})
            WHERE p.max_flow_rate IS NOT NULL
              AND p.current_flow_rate IS NOT NULL
            WITH p,
                 (p.current_flow_rate / p.max_flow_rate) * 100 as utilization
            RETURN $region as region,
                   count(p) as pipeline_count,
                   round(sum(p.max_flow_rate), 2) as total_capacity,
                   round(sum(p.current_flow_rate), 2) as current_flow,
                   round(avg(utilization), 1) as avg_utilization_percent,
                   round(max(utilization), 1) as max_utilization_percent,
                   count(CASE WHEN utilization > 80 THEN 1 END) as high_utilization_count
            """
            params = {'region': region}
        else:
            query = """
            MATCH (p:PipelineSegment)
            WHERE p.max_flow_rate IS NOT NULL
              AND p.current_flow_rate IS NOT NULL
            WITH p,
                 (p.current_flow_rate / p.max_flow_rate) * 100 as utilization
            RETURN 'all' as region,
                   count(p) as pipeline_count,
                   round(sum(p.max_flow_rate), 2) as total_capacity,
                   round(sum(p.current_flow_rate), 2) as current_flow,
                   round(avg(utilization), 1) as avg_utilization_percent,
                   round(max(utilization), 1) as max_utilization_percent,
                   count(CASE WHEN utilization > 80 THEN 1 END) as high_utilization_count
            """
            params = {}
        
        result = self.conn.execute_query(query, **params)
        return result[0] if result else {}
    
    def find_alternative_routes(
        self,
        from_id: str,
        to_id: str,
        max_routes: int = 3
    ) -> List[Dict[str, Any]]:
        """Find alternative routes between two points."""
        query = """
        MATCH (from:PipelineSegment {id: $from_id})
        MATCH (to:PipelineSegment {id: $to_id})
        MATCH path = (from)-[:CONNECTS_TO*1..10]-(to)
        WITH path,
             [n IN nodes(path) | n.id] as node_ids,
             [r IN relationships(path) | coalesce(r.length_m, 0)] as lengths,
             [n IN nodes(path) | coalesce(n.max_flow_rate, 1000.0)] as capacities
        RETURN node_ids,
               reduce(total = 0, l IN lengths | total + l) as total_length,
               min([c IN capacities | c]) as min_capacity
        ORDER BY total_length ASC
        LIMIT $max_routes
        """
        result = self.conn.execute_query(
            query,
            from_id=from_id,
            to_id=to_id,
            max_routes=max_routes
        )
        return result
    
    def simulate_outage_impact(
        self,
        pipeline_id: str
    ) -> Dict[str, Any]:
        """Simulate the impact of taking a pipeline segment out of service."""
        query = """
        MATCH (p:PipelineSegment {id: $pipeline_id})
        
        // Find customers potentially affected
        MATCH (p)-[:CONNECTS_TO*1..5]-(downstream)-[:CONNECTS_TO*]-(meter:Meter)
              -[:MEASURES]->(customer:Customer)
        WITH p, count(DISTINCT customer) as affected_customers
        
        // Find alternative paths that bypass this segment
        MATCH (upstream)-[:CONNECTS_TO]-(p)-[:CONNECTS_TO]-(downstream_pipe)
        OPTIONAL MATCH alt_path = (upstream)-[:CONNECTS_TO*2..8]-(downstream_pipe)
        WHERE NONE(n IN nodes(alt_path) WHERE n = p)
        
        RETURN p.id as pipeline_id,
               p.location as location,
               affected_customers,
               count(DISTINCT alt_path) as alternative_paths,
               CASE
                 WHEN count(DISTINCT alt_path) = 0 THEN 'critical'
                 WHEN count(DISTINCT alt_path) < 2 THEN 'high'
                 ELSE 'medium'
               END as impact_severity
        """
        result = self.conn.execute_query(query, pipeline_id=pipeline_id)
        return result[0] if result else {}
    
    def optimize_pressure_distribution(
        self,
        region: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze pressure distribution and recommend optimizations.
        Returns segments that could benefit from pressure adjustments.
        """
        region_filter = "WHERE p.region = $region" if region else ""
        
        query = f"""
        MATCH (p:PipelineSegment)
        {region_filter}
        WHERE p.current_pressure_bar IS NOT NULL
          AND p.max_pressure_bar IS NOT NULL
        WITH p,
             (p.current_pressure_bar / p.max_pressure_bar) * 100 as pressure_utilization
        
        // Find segments with suboptimal pressure
        WITH p, pressure_utilization
        WHERE pressure_utilization < 70 OR pressure_utilization > 95
        
        RETURN p.id as pipeline_id,
               p.location as location,
               p.current_pressure_bar as current_pressure,
               p.max_pressure_bar as max_pressure,
               round(pressure_utilization, 1) as utilization_percent,
               CASE
                 WHEN pressure_utilization < 70 THEN 'increase_pressure'
                 WHEN pressure_utilization > 95 THEN 'decrease_pressure'
               END as recommendation
        ORDER BY abs(pressure_utilization - 85) DESC
        LIMIT 20
        """
        
        params = {'region': region} if region else {}
        result = self.conn.execute_query(query, **params)
        
        return {
            'region': region or 'all',
            'optimization_opportunities': len(result),
            'recommendations': result
        }
    
    def calculate_network_resilience(self) -> Dict[str, Any]:
        """
        Calculate network resilience score based on connectivity and redundancy.
        Higher score = more resilient network.
        """
        query = """
        // Calculate basic topology metrics
        MATCH (p:PipelineSegment)
        WITH count(p) as total_nodes
        
        MATCH ()-[r:CONNECTS_TO]->()
        WITH total_nodes, count(r) as total_edges
        
        // Calculate average degree (connections per node)
        WITH total_nodes, total_edges,
             toFloat(total_edges) / total_nodes as avg_degree
        
        // Find critical points (nodes whose removal would disconnect network)
        MATCH (p:PipelineSegment)
        OPTIONAL MATCH (p)-[r:CONNECTS_TO]-()
        WITH total_nodes, total_edges, avg_degree,
             count(CASE WHEN size((p)-[:CONNECTS_TO]-()) = 1 THEN 1 END) as leaf_nodes
        
        // Calculate resilience score (0-100)
        WITH total_nodes, total_edges, avg_degree, leaf_nodes,
             (avg_degree / 4.0) * 40 as connectivity_score,
             ((total_nodes - leaf_nodes) / toFloat(total_nodes)) * 40 as redundancy_score,
             CASE 
               WHEN total_edges > total_nodes * 1.5 THEN 20
               WHEN total_edges > total_nodes THEN 15
               ELSE 10
             END as topology_score
        
        RETURN round(connectivity_score + redundancy_score + topology_score, 1) as resilience_score,
               total_nodes,
               total_edges,
               round(avg_degree, 2) as avg_degree,
               leaf_nodes,
               round(connectivity_score, 1) as connectivity_component,
               round(redundancy_score, 1) as redundancy_component,
               topology_score
        """
        result = self.conn.execute_query(query)
        return result[0] if result else {}
    
    def find_critical_junctions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Identify critical junction points (highly connected nodes).
        These are strategically important for network operation.
        """
        query = """
        MATCH (p:PipelineSegment)
        OPTIONAL MATCH (p)-[r:CONNECTS_TO]-()
        WITH p, count(r) as connection_count
        WHERE connection_count > 2
        
        OPTIONAL MATCH (p)-[:CONNECTS_TO*1..3]-(customer_meter:Meter)
              -[:MEASURES]->(c:Customer)
        WITH p, connection_count, count(DISTINCT c) as downstream_customers
        
        RETURN p.id as pipeline_id,
               p.location as location,
               connection_count,
               downstream_customers,
               round((connection_count * 0.4 + downstream_customers * 0.6), 1) as criticality_score
        ORDER BY criticality_score DESC
        LIMIT $limit
        """
        result = self.conn.execute_query(query, limit=limit)
        return result
