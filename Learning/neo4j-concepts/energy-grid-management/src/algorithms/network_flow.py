"""
Network Flow Algorithms for Energy Grid
Analyze power flow and network capacity.
"""

from typing import List, Dict, Any, Optional
from neo4j import Driver


class NetworkFlowAlgorithms:
    """Network flow and capacity analysis algorithms."""
    
    def __init__(self, driver: Driver):
        """Initialize with Neo4j driver."""
        self.driver = driver
    
    def calculate_max_flow(
        self,
        source_id: str,
        sink_id: str,
        capacity_property: str = "capacity_mw"
    ) -> Dict[str, Any]:
        """Calculate maximum flow from source to sink (Ford-Fulkerson concept)."""
        with self.driver.session() as session:
            # Find all paths and their bottleneck capacities
            query = """
            MATCH (source {id: $source_id}), (sink {id: $sink_id})
            MATCH path = (source)-[:CONNECTED_TO|SUPPLIES_TO*1..5]->(sink)
            WHERE ALL(r IN relationships(path) WHERE r.status <> 'inactive')
            
            WITH path,
                 reduce(min_cap = 999999.0, node IN nodes(path) | 
                     CASE 
                         WHEN $capacity_property IN keys(node) AND node[$capacity_property] < min_cap
                         THEN node[$capacity_property]
                         ELSE min_cap
                     END
                 ) as path_capacity
            
            RETURN 
                [node IN nodes(path) | node.name] as path_nodes,
                path_capacity,
                length(path) as path_length
            ORDER BY path_capacity DESC, path_length ASC
            """
            
            result = session.run(
                query,
                source_id=source_id,
                sink_id=sink_id,
                capacity_property=capacity_property
            )
            paths = [dict(record) for record in result]
            
            # Calculate total max flow (sum of non-overlapping paths)
            max_flow = sum(p["path_capacity"] for p in paths[:3])  # Top 3 paths
            
            return {
                "source_id": source_id,
                "sink_id": sink_id,
                "max_flow_mw": max_flow,
                "paths": paths,
                "path_count": len(paths)
            }
    
    def identify_bottlenecks(self, threshold_utilization: float = 0.8) -> List[Dict[str, Any]]:
        """Identify transmission lines operating near capacity."""
        with self.driver.session() as session:
            query = """
            MATCH (tl:TransmissionLine)
            WHERE tl.status = 'active'
            
            MATCH (from)-[:CONNECTS]->(tl)-[:CONNECTS]->(to)
            
            // Estimate load based on downstream customers
            OPTIONAL MATCH (to)-[:SUPPLIES_TO*0..2]->(c:Customer)
            WITH tl, from, to, 
                 sum(c.consumption_mw) as downstream_load,
                 tl.capacity_mw * (1 - tl.loss_percent / 100.0) as effective_capacity
            
            WITH tl, from, to, downstream_load, effective_capacity,
                 downstream_load / effective_capacity as utilization
            
            WHERE utilization >= $threshold
            
            RETURN 
                tl.id as line_id,
                tl.name as line_name,
                from.name as from_substation,
                to.name as to_substation,
                tl.capacity_mw as rated_capacity,
                effective_capacity,
                downstream_load as estimated_load,
                utilization,
                tl.loss_percent,
                CASE 
                    WHEN utilization >= 0.95 THEN 'CRITICAL'
                    WHEN utilization >= 0.85 THEN 'HIGH'
                    ELSE 'MODERATE'
                END as risk_level
            ORDER BY utilization DESC
            """
            
            result = session.run(query, threshold=threshold_utilization)
            return [dict(record) for record in result]
    
    def analyze_network_capacity(self) -> Dict[str, Any]:
        """Analyze overall network capacity and utilization."""
        with self.driver.session() as session:
            query = """
            // Generation capacity
            MATCH (pp:PowerPlant {status: 'operational'})
            WITH sum(pp.capacity_mw) as total_generation_capacity
            
            // Transmission capacity
            MATCH (tl:TransmissionLine {status: 'active'})
            WITH total_generation_capacity,
                 sum(tl.capacity_mw) as total_transmission_capacity,
                 avg(tl.loss_percent) as avg_transmission_loss
            
            // Distribution capacity
            MATCH (ss:Substation {status: 'operational'})
            WITH total_generation_capacity, total_transmission_capacity, avg_transmission_loss,
                 sum(ss.capacity_mva) as total_distribution_capacity
            
            // Total load
            MATCH (c:Customer)
            WITH total_generation_capacity, total_transmission_capacity, 
                 avg_transmission_loss, total_distribution_capacity,
                 sum(c.consumption_mw) as total_load
            
            RETURN 
                total_generation_capacity,
                total_transmission_capacity,
                total_distribution_capacity,
                total_load,
                avg_transmission_loss,
                (total_load / total_generation_capacity) as generation_utilization,
                (total_generation_capacity - total_load) as generation_reserve_mw,
                ((total_generation_capacity - total_load) / total_generation_capacity) as reserve_margin
            """
            
            result = session.run(query)
            record = result.single()
            return dict(record) if record else {}
    
    def find_redundant_paths(
        self,
        source_id: str,
        target_id: str,
        min_paths: int = 2
    ) -> Dict[str, Any]:
        """Find redundant paths for reliability analysis."""
        with self.driver.session() as session:
            query = """
            MATCH (source {id: $source_id}), (target {id: $target_id})
            MATCH paths = allShortestPaths((source)-[:CONNECTED_TO*]-(target))
            WHERE ALL(r IN relationships(paths) WHERE r.status <> 'inactive')
            
            WITH paths
            LIMIT 10
            
            RETURN 
                count(paths) as path_count,
                collect([node IN nodes(paths) | node.name]) as path_nodes,
                avg(length(paths)) as avg_path_length
            """
            
            result = session.run(query, source_id=source_id, target_id=target_id)
            record = result.single()
            
            if not record:
                return {"redundancy": "NONE", "path_count": 0}
            
            path_count = record["path_count"]
            
            return {
                "source_id": source_id,
                "target_id": target_id,
                "path_count": path_count,
                "paths": record["path_nodes"],
                "avg_path_length": record["avg_path_length"],
                "redundancy": "HIGH" if path_count >= min_paths else "LOW",
                "reliability_score": min(path_count / min_paths, 1.0)
            }
    
    def calculate_load_distribution(self) -> List[Dict[str, Any]]:
        """Analyze load distribution across the network."""
        with self.driver.session() as session:
            query = """
            MATCH (ss:Substation)
            OPTIONAL MATCH (ss)-[:SUPPLIES_TO]->(c:Customer)
            WITH ss, count(c) as customer_count, sum(c.consumption_mw) as total_load
            
            OPTIONAL MATCH (ss)-[:LOCATED_IN]->(l:Location)
            
            RETURN 
                ss.id as substation_id,
                ss.name as substation_name,
                ss.type as substation_type,
                ss.capacity_mva as capacity,
                l.name as location,
                customer_count,
                total_load,
                (total_load / ss.capacity_mva * 100) as utilization_pct,
                CASE 
                    WHEN total_load / ss.capacity_mva > 0.9 THEN 'OVERLOADED'
                    WHEN total_load / ss.capacity_mva > 0.7 THEN 'HIGH'
                    WHEN total_load / ss.capacity_mva > 0.5 THEN 'MODERATE'
                    ELSE 'LOW'
                END as load_level
            ORDER BY utilization_pct DESC
            """
            
            result = session.run(query)
            return [dict(record) for record in result]
    
    def simulate_outage_impact(
        self,
        component_id: str,
        component_type: str
    ) -> Dict[str, Any]:
        """Simulate impact of a component outage on network flow."""
        with self.driver.session() as session:
            # Find affected customers
            query = f"""
            MATCH (component:{component_type} {{id: $component_id}})
            
            // Direct customers
            OPTIONAL MATCH (component)-[:SUPPLIES_TO]->(direct:Customer)
            WITH component, collect(direct) as direct_customers
            
            // Customers through connected substations
            OPTIONAL MATCH path = (component)-[:CONNECTED_TO*1..2]->(ss:Substation)-[:SUPPLIES_TO]->(indirect:Customer)
            WHERE ALL(r IN relationships(path) WHERE r.status <> 'inactive')
            WITH component, direct_customers, collect(DISTINCT indirect) as indirect_customers
            
            // Combine and remove duplicates
            WITH component, direct_customers + 
                 [c IN indirect_customers WHERE NOT c IN direct_customers] as all_affected
            
            RETURN 
                component.id as component_id,
                component.name as component_name,
                size(all_affected) as affected_customers,
                reduce(load = 0.0, c IN all_affected | load + c.consumption_mw) as affected_load_mw,
                [c IN all_affected | {{
                    id: c.id,
                    name: c.name,
                    type: c.type,
                    consumption_mw: c.consumption_mw
                }}] as customer_details
            """
            
            result = session.run(query, component_id=component_id)
            impact = result.single()
            
            if not impact:
                return {}
            
            # Find alternative supply routes
            alt_routes_query = """
            MATCH (component {id: $component_id})
            MATCH (component)-[:SUPPLIES_TO|CONNECTED_TO*1..2]->(affected:Customer)
            
            // Find other substations that could supply these customers
            MATCH (alternative:Substation {status: 'operational'})
            WHERE alternative.id <> $component_id
            
            MATCH path = shortestPath((alternative)-[:CONNECTED_TO*..4]-(affected))
            WHERE NONE(node IN nodes(path) WHERE node.id = $component_id)
            
            RETURN 
                count(DISTINCT affected) as reroutable_customers,
                sum(affected.consumption_mw) as reroutable_load_mw
            """
            
            reroute_result = session.run(alt_routes_query, component_id=component_id)
            reroute_record = reroute_result.single()
            
            return {
                **dict(impact),
                "reroute_analysis": dict(reroute_record) if reroute_record else {},
                "impact_severity": self._calculate_impact_severity(
                    impact["affected_customers"],
                    impact["affected_load_mw"]
                )
            }
    
    def optimize_power_flow(self) -> List[Dict[str, Any]]:
        """Suggest power flow optimizations."""
        with self.driver.session() as session:
            # Find underutilized generation
            underutilized_query = """
            MATCH (pp:PowerPlant {status: 'operational'})
            MATCH (pp)-[:SUPPLIES_TO|CONNECTED_TO*1..3]->(c:Customer)
            WITH pp, sum(c.consumption_mw) as current_supply
            WHERE current_supply < pp.capacity_mw * 0.5
            
            OPTIONAL MATCH (pp)-[:LOCATED_IN]->(l:Location)
            
            RETURN 
                pp.id as plant_id,
                pp.name as plant_name,
                pp.type as plant_type,
                pp.capacity_mw as capacity,
                current_supply,
                (current_supply / pp.capacity_mw * 100) as utilization_pct,
                (pp.capacity_mw - current_supply) as available_capacity,
                l.name as location
            ORDER BY available_capacity DESC
            """
            
            result = session.run(underutilized_query)
            return [dict(record) for record in result]
    
    def _calculate_impact_severity(
        self,
        affected_customers: int,
        affected_load_mw: float
    ) -> str:
        """Calculate impact severity level."""
        if affected_customers > 100 or affected_load_mw > 50:
            return "CRITICAL"
        elif affected_customers > 50 or affected_load_mw > 20:
            return "HIGH"
        elif affected_customers > 10 or affected_load_mw > 5:
            return "MEDIUM"
        else:
            return "LOW"
