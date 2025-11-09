"""
Analytics Repository for Energy Grid Management
Handles complex analytical queries and aggregations.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from neo4j import Session


class AnalyticsRepository:
    """Repository for analytics and reporting operations."""
    
    def __init__(self, session: Session):
        """Initialize with Neo4j session."""
        self.session = session
    
    # GRID PERFORMANCE ANALYTICS
    
    def get_grid_health_score(self) -> Dict[str, Any]:
        """Calculate overall grid health score."""
        query = """
        // Get power plant health
        MATCH (pp:PowerPlant)
        WITH 
            count(pp) as total_plants,
            count(CASE WHEN pp.status = 'operational' THEN 1 END) as operational_plants,
            sum(pp.capacity_mw) as total_capacity,
            sum(CASE WHEN pp.status = 'operational' THEN pp.capacity_mw ELSE 0 END) as available_capacity
        
        // Get substation health
        MATCH (ss:Substation)
        WITH total_plants, operational_plants, total_capacity, available_capacity,
            count(ss) as total_substations,
            count(CASE WHEN ss.status = 'operational' THEN 1 END) as operational_substations
        
        // Get transmission line health
        MATCH (tl:TransmissionLine)
        WITH total_plants, operational_plants, total_capacity, available_capacity,
            total_substations, operational_substations,
            count(tl) as total_lines,
            count(CASE WHEN tl.status = 'active' THEN 1 END) as active_lines
        
        // Get active incidents
        MATCH (i:Incident)
        WHERE i.status IN ['reported', 'investigating', 'in_progress']
        WITH total_plants, operational_plants, total_capacity, available_capacity,
            total_substations, operational_substations, total_lines, active_lines,
            count(i) as active_incidents,
            count(CASE WHEN i.severity = 'critical' THEN 1 END) as critical_incidents
        
        RETURN 
            (operational_plants * 1.0 / total_plants * 100) as plant_health_pct,
            (operational_substations * 1.0 / total_substations * 100) as substation_health_pct,
            (active_lines * 1.0 / total_lines * 100) as line_health_pct,
            (available_capacity / total_capacity * 100) as capacity_health_pct,
            active_incidents,
            critical_incidents,
            ((operational_plants * 1.0 / total_plants * 0.3) +
             (operational_substations * 1.0 / total_substations * 0.3) +
             (active_lines * 1.0 / total_lines * 0.2) +
             (available_capacity / total_capacity * 0.2)) * 100 as overall_health_score
        """
        
        result = self.session.run(query)
        record = result.single()
        return dict(record) if record else {}
    
    def get_capacity_analysis(self) -> Dict[str, Any]:
        """Analyze grid capacity and utilization."""
        query = """
        MATCH (pp:PowerPlant)
        WITH 
            sum(pp.capacity_mw) as total_capacity,
            sum(CASE WHEN pp.status = 'operational' THEN pp.capacity_mw ELSE 0 END) as available_capacity,
            sum(CASE WHEN pp.type IN ['solar', 'wind', 'hydro'] THEN pp.capacity_mw ELSE 0 END) as renewable_capacity
        
        MATCH (c:Customer)
        WITH total_capacity, available_capacity, renewable_capacity,
            sum(c.consumption_mw) as total_consumption,
            sum(CASE WHEN c.type = 'residential' THEN c.consumption_mw ELSE 0 END) as residential_consumption,
            sum(CASE WHEN c.type = 'commercial' THEN c.consumption_mw ELSE 0 END) as commercial_consumption,
            sum(CASE WHEN c.type = 'industrial' THEN c.consumption_mw ELSE 0 END) as industrial_consumption
        
        RETURN 
            total_capacity,
            available_capacity,
            renewable_capacity,
            (renewable_capacity / total_capacity * 100) as renewable_pct,
            total_consumption,
            (total_consumption / available_capacity * 100) as utilization_pct,
            (available_capacity - total_consumption) as reserve_capacity,
            ((available_capacity - total_consumption) / available_capacity * 100) as reserve_pct,
            residential_consumption,
            commercial_consumption,
            industrial_consumption
        """
        
        result = self.session.run(query)
        record = result.single()
        return dict(record) if record else {}
    
    def get_regional_performance(self) -> List[Dict[str, Any]]:
        """Analyze performance by region."""
        query = """
        MATCH (l:Location)
        OPTIONAL MATCH (l)<-[:LOCATED_IN]-(pp:PowerPlant)
        WITH l, 
            count(pp) as plant_count,
            sum(pp.capacity_mw) as total_capacity,
            sum(CASE WHEN pp.status = 'operational' THEN pp.capacity_mw ELSE 0 END) as available_capacity,
            sum(CASE WHEN pp.type IN ['solar', 'wind', 'hydro'] THEN pp.capacity_mw ELSE 0 END) as renewable_capacity
        
        OPTIONAL MATCH (l)<-[:LOCATED_IN]-(ss:Substation)
        WITH l, plant_count, total_capacity, available_capacity, renewable_capacity,
            count(ss) as substation_count,
            count(CASE WHEN ss.status = 'operational' THEN 1 END) as operational_substations
        
        OPTIONAL MATCH (l)<-[:LOCATED_IN]-(c:Customer)
        WITH l, plant_count, total_capacity, available_capacity, renewable_capacity,
            substation_count, operational_substations,
            count(c) as customer_count,
            sum(c.consumption_mw) as total_consumption
        
        RETURN 
            l.name as region,
            l.state as state,
            plant_count,
            total_capacity,
            available_capacity,
            renewable_capacity,
            (renewable_capacity / total_capacity * 100) as renewable_pct,
            substation_count,
            operational_substations,
            customer_count,
            total_consumption,
            (total_consumption / available_capacity * 100) as utilization_pct
        ORDER BY total_capacity DESC
        """
        
        result = self.session.run(query)
        return [dict(record) for record in result]
    
    # NETWORK TOPOLOGY ANALYTICS
    
    def get_network_connectivity_metrics(self) -> Dict[str, Any]:
        """Analyze network connectivity and resilience."""
        query = """
        // Count all substations
        MATCH (ss:Substation)
        WITH count(ss) as total_substations
        
        // Find isolated substations
        MATCH (isolated:Substation)
        WHERE NOT (isolated)-[:CONNECTED_TO]-(:Substation)
        WITH total_substations, count(isolated) as isolated_substations
        
        // Find substations with single connection (vulnerable)
        MATCH (vulnerable:Substation)-[r:CONNECTED_TO]-(:Substation)
        WITH total_substations, isolated_substations,
            count(DISTINCT vulnerable) as substations_with_connections
        WHERE size([(vulnerable)-[:CONNECTED_TO]-() | 1]) = 1
        WITH total_substations, isolated_substations, 
            count(DISTINCT vulnerable) as vulnerable_substations
        
        // Count transmission lines
        MATCH (tl:TransmissionLine)
        WITH total_substations, isolated_substations, vulnerable_substations,
            count(tl) as total_lines,
            count(CASE WHEN tl.status = 'active' THEN 1 END) as active_lines,
            avg(tl.loss_percent) as avg_line_loss
        
        // Calculate average path length
        MATCH path = shortestPath((s1:Substation)-[:CONNECTED_TO*]-(s2:Substation))
        WHERE s1.id < s2.id
        WITH total_substations, isolated_substations, vulnerable_substations,
            total_lines, active_lines, avg_line_loss,
            avg(length(path)) as avg_path_length
        
        RETURN 
            total_substations,
            isolated_substations,
            vulnerable_substations,
            (vulnerable_substations * 1.0 / total_substations * 100) as vulnerability_pct,
            total_lines,
            active_lines,
            (active_lines * 1.0 / total_lines * 100) as line_availability_pct,
            avg_line_loss,
            avg_path_length,
            (total_lines * 1.0 / total_substations) as avg_connections_per_substation
        """
        
        result = self.session.run(query)
        record = result.single()
        return dict(record) if record else {}
    
    def identify_critical_substations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Identify most critical substations using graph centrality."""
        query = """
        MATCH (ss:Substation)
        OPTIONAL MATCH (ss)-[:SUPPLIES_TO]->(c:Customer)
        WITH ss, count(c) as customer_count, sum(c.consumption_mw) as total_consumption
        
        OPTIONAL MATCH (ss)-[conn:CONNECTED_TO]-(:Substation)
        WITH ss, customer_count, total_consumption, count(conn) as connection_count
        
        // Calculate criticality score
        WITH ss, customer_count, total_consumption, connection_count,
            (customer_count * 0.4 + 
             total_consumption * 0.4 + 
             connection_count * 0.2) as criticality_score
        
        RETURN 
            ss.id as substation_id,
            ss.name as substation_name,
            ss.type as substation_type,
            customer_count,
            total_consumption,
            connection_count,
            criticality_score
        ORDER BY criticality_score DESC
        LIMIT $limit
        """
        
        result = self.session.run(query, limit=limit)
        return [dict(record) for record in result]
    
    def find_transmission_bottlenecks(self) -> List[Dict[str, Any]]:
        """Find transmission lines operating at high capacity."""
        query = """
        MATCH (tl:TransmissionLine)
        WHERE tl.status = 'active'
        WITH tl,
            (tl.capacity_mw * (1 - tl.loss_percent / 100.0)) as effective_capacity
        
        MATCH (from:Substation)-[:CONNECTS]->(tl)
        MATCH (tl)-[:CONNECTS]->(to:Substation)
        
        // Estimate load based on downstream customers
        OPTIONAL MATCH (to)-[:SUPPLIES_TO]->(c:Customer)
        WITH tl, from, to, effective_capacity,
            sum(c.consumption_mw) as downstream_load
        
        WITH tl, from, to, effective_capacity, downstream_load,
            (downstream_load / effective_capacity * 100) as utilization_pct
        
        WHERE utilization_pct > 70
        
        RETURN 
            tl.id as line_id,
            tl.name as line_name,
            from.name as from_substation,
            to.name as to_substation,
            tl.capacity_mw as rated_capacity,
            effective_capacity,
            downstream_load as estimated_load,
            utilization_pct,
            tl.loss_percent,
            CASE 
                WHEN utilization_pct > 90 THEN 'CRITICAL'
                WHEN utilization_pct > 80 THEN 'HIGH'
                ELSE 'MODERATE'
            END as risk_level
        ORDER BY utilization_pct DESC
        """
        
        result = self.session.run(query)
        return [dict(record) for record in result]
    
    # CUSTOMER ANALYTICS
    
    def get_customer_segmentation(self) -> List[Dict[str, Any]]:
        """Analyze customer base by type and consumption."""
        query = """
        MATCH (c:Customer)
        WITH c.type as customer_type, c
        RETURN 
            customer_type,
            count(c) as customer_count,
            sum(c.consumption_mw) as total_consumption,
            avg(c.consumption_mw) as avg_consumption,
            min(c.consumption_mw) as min_consumption,
            max(c.consumption_mw) as max_consumption,
            (sum(c.consumption_mw) * 1.0 / 
             (SELECT sum(consumption_mw) FROM (MATCH (all:Customer) RETURN all)) * 100) 
             as consumption_share_pct
        ORDER BY total_consumption DESC
        """
        
        result = self.session.run(query)
        return [dict(record) for record in result]
    
    def identify_high_value_customers(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Identify highest consuming customers."""
        query = """
        MATCH (c:Customer)
        OPTIONAL MATCH (c)<-[:SUPPLIES_TO]-(ss:Substation)
        
        RETURN 
            c.id as customer_id,
            c.name as customer_name,
            c.type as customer_type,
            c.consumption_mw,
            ss.name as serving_substation,
            ss.type as substation_type,
            c.consumption_mw * 730 as estimated_annual_mwh  // 730 hours/month average
        ORDER BY c.consumption_mw DESC
        LIMIT $limit
        """
        
        result = self.session.run(query, limit=limit)
        return [dict(record) for record in result]
    
    # RELIABILITY METRICS
    
    def calculate_reliability_metrics(self, days: int = 30) -> Dict[str, Any]:
        """Calculate grid reliability metrics (SAIFI, SAIDI, CAIDI)."""
        query = """
        // Get total customers
        MATCH (c:Customer)
        WITH count(c) as total_customers
        
        // Get incidents in time period
        MATCH (i:Incident)
        WHERE i.reported_at >= datetime() - duration({days: $days})
          AND i.status = 'resolved'
          AND i.resolved_at IS NOT NULL
        
        WITH total_customers, i,
            duration.inSeconds(i.reported_at, i.resolved_at).minutes as duration_minutes
        
        WITH total_customers,
            sum(i.affected_customers) as total_interrupted_customers,
            sum(i.affected_customers * duration_minutes) as total_customer_minutes
        
        RETURN 
            total_customers,
            total_interrupted_customers,
            total_customer_minutes,
            (total_interrupted_customers * 1.0 / total_customers) as SAIFI,  // System Average Interruption Frequency Index
            (total_customer_minutes / total_customers) as SAIDI,  // System Average Interruption Duration Index
            (total_customer_minutes / total_interrupted_customers) as CAIDI  // Customer Average Interruption Duration Index
        """
        
        result = self.session.run(query, days=days)
        record = result.single()
        return dict(record) if record else {}
    
    # TREND ANALYSIS
    
    def get_consumption_trends(self, days: int = 30) -> List[Dict[str, Any]]:
        """Analyze consumption trends (simulated with current data)."""
        query = """
        MATCH (c:Customer)
        WITH c.type as customer_type,
            sum(c.consumption_mw) as current_consumption,
            count(c) as customer_count
        
        RETURN 
            customer_type,
            customer_count,
            current_consumption,
            current_consumption * 0.98 as projected_consumption_30d,  // 2% growth
            current_consumption * 1.10 as projected_consumption_1y,   // 10% annual growth
            current_consumption * 1.25 as projected_consumption_5y    // 25% 5-year growth
        ORDER BY current_consumption DESC
        """
        
        result = self.session.run(query, days=days)
        return [dict(record) for record in result]
    
    def get_renewable_energy_trends(self) -> Dict[str, Any]:
        """Analyze renewable energy statistics."""
        query = """
        MATCH (pp:PowerPlant)
        WITH 
            sum(pp.capacity_mw) as total_capacity,
            sum(CASE WHEN pp.type = 'solar' THEN pp.capacity_mw ELSE 0 END) as solar_capacity,
            sum(CASE WHEN pp.type = 'wind' THEN pp.capacity_mw ELSE 0 END) as wind_capacity,
            sum(CASE WHEN pp.type = 'hydro' THEN pp.capacity_mw ELSE 0 END) as hydro_capacity,
            sum(CASE WHEN pp.type = 'natural_gas' THEN pp.capacity_mw ELSE 0 END) as gas_capacity,
            sum(CASE WHEN pp.type = 'coal' THEN pp.capacity_mw ELSE 0 END) as coal_capacity,
            sum(CASE WHEN pp.type = 'nuclear' THEN pp.capacity_mw ELSE 0 END) as nuclear_capacity,
            count(CASE WHEN pp.type IN ['solar', 'wind', 'hydro'] THEN 1 END) as renewable_plant_count,
            count(pp) as total_plant_count
        
        RETURN 
            total_capacity,
            solar_capacity,
            wind_capacity,
            hydro_capacity,
            (solar_capacity + wind_capacity + hydro_capacity) as total_renewable_capacity,
            ((solar_capacity + wind_capacity + hydro_capacity) / total_capacity * 100) as renewable_pct,
            gas_capacity,
            coal_capacity,
            nuclear_capacity,
            renewable_plant_count,
            total_plant_count
        """
        
        result = self.session.run(query)
        record = result.single()
        return dict(record) if record else {}
