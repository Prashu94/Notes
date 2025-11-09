"""Repository for infrastructure operations (pipelines, meters, sensors, etc.)."""

from typing import List, Dict, Any, Optional
from datetime import datetime

from ..connection import Neo4jConnection
from ..models.pipeline import PipelineSegment, PipelineType, PipelineStatus
from ..models.meter import Meter, MeterType, MeterStatus


class InfrastructureRepository:
    """Repository for managing utility infrastructure."""
    
    def __init__(self):
        """Initialize repository with database connection."""
        self.conn = Neo4jConnection()
    
    # Pipeline operations
    def create_pipeline(self, pipeline: PipelineSegment) -> str:
        """Create a new pipeline segment."""
        query = """
        CREATE (p:PipelineSegment $props)
        RETURN p.id as id
        """
        result = self.conn.execute_query(query, props=pipeline.to_neo4j_properties())
        return result[0]['id'] if result else None
    
    def get_pipeline(self, pipeline_id: str) -> Optional[Dict[str, Any]]:
        """Get pipeline by ID."""
        query = """
        MATCH (p:PipelineSegment {id: $pipeline_id})
        RETURN p
        """
        result = self.conn.execute_query(query, pipeline_id=pipeline_id)
        return dict(result[0]['p']) if result else None
    
    def update_pipeline(self, pipeline_id: str, updates: Dict[str, Any]) -> bool:
        """Update pipeline properties."""
        query = """
        MATCH (p:PipelineSegment {id: $pipeline_id})
        SET p += $updates
        RETURN p.id as id
        """
        result = self.conn.execute_query(query, pipeline_id=pipeline_id, updates=updates)
        return len(result) > 0
    
    def get_pipelines_by_region(self, region: str) -> List[Dict[str, Any]]:
        """Get all pipelines in a region."""
        query = """
        MATCH (p:PipelineSegment {region: $region})
        RETURN p
        ORDER BY p.id
        """
        result = self.conn.execute_query(query, region=region)
        return [dict(r['p']) for r in result]
    
    def get_pipelines_by_type(self, pipeline_type: str) -> List[Dict[str, Any]]:
        """Get pipelines by type (water/gas)."""
        query = """
        MATCH (p:PipelineSegment {type: $pipeline_type})
        RETURN p
        ORDER BY p.region, p.id
        """
        result = self.conn.execute_query(query, pipeline_type=pipeline_type)
        return [dict(r['p']) for r in result]
    
    def get_high_risk_pipelines(self, risk_threshold: float = 60.0) -> List[Dict[str, Any]]:
        """Get pipelines with high risk score."""
        query = """
        MATCH (p:PipelineSegment)
        WHERE p.age_years > 30 OR p.status = 'maintenance' OR p.status = 'failed'
        RETURN p, p.age_years as age
        ORDER BY age DESC
        """
        result = self.conn.execute_query(query)
        return [dict(r['p']) for r in result]
    
    def get_pipelines_needing_inspection(self) -> List[Dict[str, Any]]:
        """Get pipelines that need inspection."""
        query = """
        MATCH (p:PipelineSegment)
        WHERE p.last_inspection_date IS NULL
           OR duration.between(date(p.last_inspection_date), date()).days > 365
        RETURN p, coalesce(p.last_inspection_date, 'never') as last_inspection
        ORDER BY last_inspection
        """
        result = self.conn.execute_query(query)
        return [dict(r['p']) for r in result]
    
    def get_pressure_anomalies(self) -> List[Dict[str, Any]]:
        """Find pipelines with abnormal pressure."""
        query = """
        MATCH (p:PipelineSegment)
        WHERE p.current_pressure_bar IS NOT NULL
          AND (p.current_pressure_bar < p.max_pressure_bar * 0.8
           OR  p.current_pressure_bar > p.max_pressure_bar)
        RETURN p, p.current_pressure_bar as pressure, p.max_pressure_bar as max_pressure
        ORDER BY pressure
        """
        result = self.conn.execute_query(query)
        return [dict(r['p']) for r in result]
    
    def connect_pipelines(self, from_id: str, to_id: str, properties: Optional[Dict[str, Any]] = None) -> bool:
        """Create CONNECTS_TO relationship between pipelines."""
        query = """
        MATCH (from:PipelineSegment {id: $from_id})
        MATCH (to:PipelineSegment {id: $to_id})
        MERGE (from)-[r:CONNECTS_TO]->(to)
        SET r += $props
        RETURN from.id as from_id, to.id as to_id
        """
        props = properties or {}
        result = self.conn.execute_query(query, from_id=from_id, to_id=to_id, props=props)
        return len(result) > 0
    
    def trace_pipeline_path(self, from_id: str, to_id: str, max_hops: int = 10) -> List[Dict[str, Any]]:
        """Find path between two pipeline segments."""
        query = """
        MATCH path = shortestPath(
            (start:PipelineSegment {id: $from_id})-[:CONNECTS_TO*1..{max_hops}]->(end:PipelineSegment {id: $to_id})
        )
        RETURN [n IN nodes(path) | n.id] as pipeline_ids,
               length(path) as hops
        """.format(max_hops=max_hops)
        result = self.conn.execute_query(query, from_id=from_id, to_id=to_id)
        return result
    
    # Meter operations
    def create_meter(self, meter: Meter) -> str:
        """Create a new meter."""
        query = """
        CREATE (m:Meter $props)
        RETURN m.id as id
        """
        result = self.conn.execute_query(query, props=meter.to_neo4j_properties())
        return result[0]['id'] if result else None
    
    def get_meter(self, meter_id: str) -> Optional[Dict[str, Any]]:
        """Get meter by ID."""
        query = """
        MATCH (m:Meter {id: $meter_id})
        RETURN m
        """
        result = self.conn.execute_query(query, meter_id=meter_id)
        return dict(result[0]['m']) if result else None
    
    def update_meter_reading(self, meter_id: str, value: float, timestamp: Optional[datetime] = None) -> bool:
        """Update meter reading."""
        if timestamp is None:
            timestamp = datetime.now()
        
        query = """
        MATCH (m:Meter {id: $meter_id})
        SET m.last_reading_value = $value,
            m.last_reading_date = $timestamp
        RETURN m.id as id
        """
        result = self.conn.execute_query(
            query,
            meter_id=meter_id,
            value=value,
            timestamp=timestamp.isoformat()
        )
        return len(result) > 0
    
    def get_meters_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Get meters by status."""
        query = """
        MATCH (m:Meter {status: $status})
        RETURN m
        ORDER BY m.id
        """
        result = self.conn.execute_query(query, status=status)
        return [dict(r['m']) for r in result]
    
    def get_stale_meters(self, max_age_hours: int = 24) -> List[Dict[str, Any]]:
        """Get meters with stale readings."""
        query = """
        MATCH (m:Meter)
        WHERE m.last_reading_date IS NOT NULL
          AND duration.between(datetime(m.last_reading_date), datetime()).hours > $max_age_hours
        RETURN m, duration.between(datetime(m.last_reading_date), datetime()).hours as hours_old
        ORDER BY hours_old DESC
        """
        result = self.conn.execute_query(query, max_age_hours=max_age_hours)
        return [dict(r['m']) for r in result]
    
    def get_low_battery_meters(self, threshold: int = 20) -> List[Dict[str, Any]]:
        """Get meters with low battery."""
        query = """
        MATCH (m:Meter)
        WHERE m.battery_level IS NOT NULL
          AND m.battery_level < $threshold
        RETURN m, m.battery_level as battery
        ORDER BY battery
        """
        result = self.conn.execute_query(query, threshold=threshold)
        return [dict(r['m']) for r in result]
    
    def link_meter_to_customer(self, meter_id: str, customer_id: str) -> bool:
        """Link meter to customer."""
        query = """
        MATCH (m:Meter {id: $meter_id})
        MATCH (c:Customer {id: $customer_id})
        MERGE (m)-[r:MEASURES]->(c)
        RETURN m.id as meter_id, c.id as customer_id
        """
        result = self.conn.execute_query(query, meter_id=meter_id, customer_id=customer_id)
        return len(result) > 0
    
    # Storage tank operations
    def create_storage_tank(self, tank_props: Dict[str, Any]) -> str:
        """Create a storage tank node."""
        query = """
        CREATE (t:StorageTank $props)
        RETURN t.id as id
        """
        result = self.conn.execute_query(query, props=tank_props)
        return result[0]['id'] if result else None
    
    def get_storage_tank(self, tank_id: str) -> Optional[Dict[str, Any]]:
        """Get storage tank by ID."""
        query = """
        MATCH (t:StorageTank {id: $tank_id})
        RETURN t
        """
        result = self.conn.execute_query(query, tank_id=tank_id)
        return dict(result[0]['t']) if result else None
    
    def get_low_capacity_tanks(self, threshold_percent: float = 30.0) -> List[Dict[str, Any]]:
        """Get tanks with low capacity."""
        query = """
        MATCH (t:StorageTank)
        WHERE t.current_level_m3 IS NOT NULL
          AND t.capacity_m3 IS NOT NULL
          AND (t.current_level_m3 * 100.0 / t.capacity_m3) < $threshold
        RETURN t, (t.current_level_m3 * 100.0 / t.capacity_m3) as fill_percent
        ORDER BY fill_percent
        """
        result = self.conn.execute_query(query, threshold=threshold_percent)
        return [dict(r['t']) for r in result]
    
    def link_tank_to_pipeline(self, tank_id: str, pipeline_id: str) -> bool:
        """Create SUPPLIES relationship from tank to pipeline."""
        query = """
        MATCH (t:StorageTank {id: $tank_id})
        MATCH (p:PipelineSegment {id: $pipeline_id})
        MERGE (t)-[r:SUPPLIES]->(p)
        RETURN t.id as tank_id, p.id as pipeline_id
        """
        result = self.conn.execute_query(query, tank_id=tank_id, pipeline_id=pipeline_id)
        return len(result) > 0
    
    # Analytics and statistics
    def get_infrastructure_statistics(self) -> Dict[str, Any]:
        """Get overall infrastructure statistics."""
        query = """
        MATCH (p:PipelineSegment)
        WITH count(p) as total_pipelines,
             sum(p.length_m) as total_length,
             avg(p.age_years) as avg_age
        MATCH (m:Meter)
        WITH total_pipelines, total_length, avg_age,
             count(m) as total_meters
        MATCH (t:StorageTank)
        RETURN total_pipelines,
               round(total_length, 2) as total_length_m,
               round(avg_age, 1) as avg_pipeline_age,
               total_meters,
               count(t) as total_tanks
        """
        result = self.conn.execute_query(query)
        return result[0] if result else {}
    
    def get_network_topology_metrics(self) -> Dict[str, Any]:
        """Calculate network topology metrics."""
        query = """
        MATCH (p:PipelineSegment)
        WITH count(p) as node_count
        MATCH ()-[r:CONNECTS_TO]->()
        WITH node_count, count(r) as edge_count
        MATCH path = (p1:PipelineSegment)-[:CONNECTS_TO*]-(p2:PipelineSegment)
        WITH node_count, edge_count, max(length(path)) as diameter
        RETURN node_count,
               edge_count,
               diameter,
               round(toFloat(edge_count) / node_count, 2) as avg_degree
        """
        result = self.conn.execute_query(query)
        return result[0] if result else {}
    
    def get_regional_infrastructure_summary(self) -> List[Dict[str, Any]]:
        """Get infrastructure summary by region."""
        query = """
        MATCH (p:PipelineSegment)
        WHERE p.region IS NOT NULL
        WITH p.region as region,
             count(p) as pipeline_count,
             sum(p.length_m) as total_length,
             avg(p.age_years) as avg_age,
             collect(DISTINCT p.type) as types
        RETURN region,
               pipeline_count,
               round(total_length, 2) as total_length_m,
               round(avg_age, 1) as avg_age,
               types
        ORDER BY pipeline_count DESC
        """
        result = self.conn.execute_query(query)
        return result
