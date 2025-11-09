"""
Infrastructure Repository

Data access layer for power grid infrastructure.
"""

import logging
from typing import List, Dict, Any, Optional
from ..connection import Neo4jConnection, get_connection
from ..models import PowerPlant, Substation

logger = logging.getLogger(__name__)


class InfrastructureRepository:
    """Repository for accessing infrastructure data."""
    
    def __init__(self, connection: Optional[Neo4jConnection] = None):
        """Initialize repository with database connection."""
        self.conn = connection or get_connection()
    
    # ===================================
    # POWER PLANT METHODS
    # ===================================
    
    def get_all_power_plants(self) -> List[Dict[str, Any]]:
        """Retrieve all power plants."""
        query = """
        MATCH (p:PowerPlant)
        RETURN p.id as id, p.name as name, p.type as type,
               p.capacity_mw as capacity_mw, p.status as status,
               p.operator as operator, p.efficiency_percent as efficiency_percent
        ORDER BY p.capacity_mw DESC
        """
        return self.conn.execute_read(query)
    
    def get_power_plant_by_id(self, plant_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve specific power plant by ID."""
        query = """
        MATCH (p:PowerPlant {id: $plant_id})
        RETURN p.id as id, p.name as name, p.type as type,
               p.capacity_mw as capacity_mw, p.status as status,
               p.operator as operator, p.efficiency_percent as efficiency_percent,
               p.commissioned_date as commissioned_date,
               p.location as location, p.emissions_tons_per_year as emissions_tons_per_year
        """
        results = self.conn.execute_read(query, {"plant_id": plant_id})
        return results[0] if results else None
    
    def get_power_plants_by_type(self, plant_type: str) -> List[Dict[str, Any]]:
        """Retrieve power plants by type."""
        query = """
        MATCH (p:PowerPlant {type: $plant_type})
        RETURN p.id as id, p.name as name, p.capacity_mw as capacity_mw,
               p.status as status, p.operator as operator
        ORDER BY p.capacity_mw DESC
        """
        return self.conn.execute_read(query, {"plant_type": plant_type})
    
    def get_renewable_plants(self) -> List[Dict[str, Any]]:
        """Retrieve all renewable energy plants."""
        query = """
        MATCH (p:PowerPlant)
        WHERE p.type IN ['solar', 'wind', 'hydro']
        RETURN p.id as id, p.name as name, p.type as type,
               p.capacity_mw as capacity_mw, p.status as status
        ORDER BY p.capacity_mw DESC
        """
        return self.conn.execute_read(query)
    
    def get_total_generation_capacity(self) -> Dict[str, float]:
        """Get total and renewable generation capacity."""
        query = """
        MATCH (p:PowerPlant)
        WITH sum(p.capacity_mw) as total_capacity
        MATCH (renewable:PowerPlant)
        WHERE renewable.type IN ['solar', 'wind', 'hydro']
        RETURN total_capacity,
               sum(renewable.capacity_mw) as renewable_capacity,
               100.0 * sum(renewable.capacity_mw) / total_capacity as renewable_percent
        """
        results = self.conn.execute_read(query)
        return results[0] if results else {}
    
    # ===================================
    # SUBSTATION METHODS
    # ===================================
    
    def get_all_substations(self) -> List[Dict[str, Any]]:
        """Retrieve all substations."""
        query = """
        MATCH (s:Substation)
        RETURN s.id as id, s.name as name, s.voltage_kv as voltage_kv,
               s.capacity_mva as capacity_mva, s.type as type,
               s.status as status, s.region as region
        ORDER BY s.capacity_mva DESC
        """
        return self.conn.execute_read(query)
    
    def get_substation_by_id(self, substation_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve specific substation by ID."""
        query = """
        MATCH (s:Substation {id: $substation_id})
        RETURN s.id as id, s.name as name, s.voltage_kv as voltage_kv,
               s.capacity_mva as capacity_mva, s.type as type,
               s.status as status, s.region as region,
               s.location as location, s.num_transformers as num_transformers
        """
        results = self.conn.execute_read(query, {"substation_id": substation_id})
        return results[0] if results else None
    
    def get_substations_by_region(self, region: str) -> List[Dict[str, Any]]:
        """Retrieve substations in a specific region."""
        query = """
        MATCH (s:Substation {region: $region})
        RETURN s.id as id, s.name as name, s.voltage_kv as voltage_kv,
               s.capacity_mva as capacity_mva, s.type as type, s.status as status
        ORDER BY s.capacity_mva DESC
        """
        return self.conn.execute_read(query, {"region": region})
    
    def get_transmission_substations(self) -> List[Dict[str, Any]]:
        """Retrieve all transmission substations."""
        query = """
        MATCH (s:Substation {type: 'transmission'})
        RETURN s.id as id, s.name as name, s.voltage_kv as voltage_kv,
               s.capacity_mva as capacity_mva, s.region as region, s.status as status
        ORDER BY s.voltage_kv DESC
        """
        return self.conn.execute_read(query)
    
    # ===================================
    # TRANSMISSION LINE METHODS
    # ===================================
    
    def get_all_transmission_lines(self) -> List[Dict[str, Any]]:
        """Retrieve all transmission lines."""
        query = """
        MATCH (s1:Substation)-[t:TRANSMITS_TO]->(s2:Substation)
        RETURN s1.id as from_id, s1.name as from_name,
               s2.id as to_id, s2.name as to_name,
               t.capacity_mw as capacity_mw, t.distance_km as distance_km,
               t.loss_percent as loss_percent, t.status as status,
               t.line_id as line_id
        ORDER BY t.capacity_mw DESC
        """
        return self.conn.execute_read(query)
    
    def get_transmission_line_by_id(self, line_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve specific transmission line."""
        query = """
        MATCH (s1:Substation)-[t:TRANSMITS_TO {line_id: $line_id}]->(s2:Substation)
        RETURN s1.id as from_id, s1.name as from_name,
               s2.id as to_id, s2.name as to_name,
               t.capacity_mw as capacity_mw, t.distance_km as distance_km,
               t.loss_percent as loss_percent, t.status as status
        """
        results = self.conn.execute_read(query, {"line_id": line_id})
        return results[0] if results else None
    
    # ===================================
    # POWER FLOW METHODS
    # ===================================
    
    def get_power_flow_from_plant(self, plant_id: str, max_hops: int = 10) -> List[Dict[str, Any]]:
        """Trace power flow from a plant to customers."""
        query = """
        MATCH path = (p:PowerPlant {id: $plant_id})-[:GENERATES]->()
                     -[:TRANSMITS_TO*0..$max_hops]->()-[:SUPPLIES_POWER]->(c:Customer)
        RETURN p.name as plant_name, c.id as customer_id, c.name as customer_name,
               c.type as customer_type, length(path) as path_length
        ORDER BY path_length, c.name
        LIMIT 50
        """
        return self.conn.execute_read(query, {"plant_id": plant_id, "max_hops": max_hops})
    
    def get_power_sources_for_customer(self, customer_id: str) -> List[Dict[str, Any]]:
        """Find all power sources serving a customer."""
        query = """
        MATCH path = (p:PowerPlant)-[:GENERATES]->()
                     -[:TRANSMITS_TO*]->()-[:SUPPLIES_POWER]->(c:Customer {id: $customer_id})
        RETURN DISTINCT p.id as plant_id, p.name as plant_name,
               p.type as plant_type, p.capacity_mw as capacity_mw,
               length(path) as path_length
        ORDER BY path_length
        """
        return self.conn.execute_read(query, {"customer_id": customer_id})
    
    def get_shortest_path_between_substations(self, from_id: str, to_id: str) -> Optional[Dict[str, Any]]:
        """Find shortest path between two substations."""
        query = """
        MATCH path = shortestPath(
            (s1:Substation {id: $from_id})-[:TRANSMITS_TO*]-(s2:Substation {id: $to_id})
        )
        RETURN [node in nodes(path) | node.name] as route,
               length(path) as hops,
               reduce(dist = 0, rel in relationships(path) | dist + rel.distance_km) as total_distance_km
        """
        results = self.conn.execute_read(query, {"from_id": from_id, "to_id": to_id})
        return results[0] if results else None
    
    # ===================================
    # CUSTOMER METHODS
    # ===================================
    
    def get_all_customers(self) -> List[Dict[str, Any]]:
        """Retrieve all customers."""
        query = """
        MATCH (c:Customer)
        RETURN c.id as id, c.name as name, c.type as type,
               c.average_consumption_kwh as average_consumption_kwh,
               c.region as region
        ORDER BY c.average_consumption_kwh DESC
        """
        return self.conn.execute_read(query)
    
    def get_customers_by_type(self, customer_type: str) -> List[Dict[str, Any]]:
        """Retrieve customers by type."""
        query = """
        MATCH (c:Customer {type: $customer_type})
        RETURN c.id as id, c.name as name,
               c.average_consumption_kwh as average_consumption_kwh,
               c.region as region
        ORDER BY c.average_consumption_kwh DESC
        """
        return self.conn.execute_read(query, {"customer_type": customer_type})
    
    def get_customers_supplied_by_substation(self, substation_id: str) -> List[Dict[str, Any]]:
        """Get all customers supplied by a substation."""
        query = """
        MATCH (s:Substation {id: $substation_id})-[:SUPPLIES_POWER]->(c:Customer)
        RETURN c.id as id, c.name as name, c.type as type,
               c.average_consumption_kwh as average_consumption_kwh
        ORDER BY c.average_consumption_kwh DESC
        """
        return self.conn.execute_read(query, {"substation_id": substation_id})
    
    # ===================================
    # STATISTICS METHODS
    # ===================================
    
    def get_system_statistics(self) -> Dict[str, Any]:
        """Get overall system statistics."""
        query = """
        MATCH (p:PowerPlant)
        WITH sum(p.capacity_mw) as total_generation
        MATCH (s:Substation)
        WITH total_generation, sum(s.capacity_mva) as total_transmission
        MATCH (c:Customer)
        WITH total_generation, total_transmission,
             sum(c.average_consumption_kwh) as total_consumption,
             count(c) as customer_count
        MATCH (plant:PowerPlant)
        WITH total_generation, total_transmission, total_consumption, customer_count,
             count(plant) as plant_count
        MATCH (sub:Substation)
        RETURN total_generation, total_transmission, total_consumption,
               customer_count, plant_count, count(sub) as substation_count
        """
        results = self.conn.execute_read(query)
        return results[0] if results else {}
    
    def get_regional_capacity(self) -> List[Dict[str, Any]]:
        """Get capacity statistics by region."""
        query = """
        MATCH (s:Substation)
        OPTIONAL MATCH (s)-[:SUPPLIES_POWER]->(c:Customer)
        WITH s.region as region,
             count(DISTINCT s) as substations,
             sum(s.capacity_mva) as total_capacity,
             count(DISTINCT c) as customers,
             sum(c.average_consumption_kwh) as total_consumption
        RETURN region, substations, total_capacity, customers, total_consumption
        ORDER BY total_capacity DESC
        """
        return self.conn.execute_read(query)
