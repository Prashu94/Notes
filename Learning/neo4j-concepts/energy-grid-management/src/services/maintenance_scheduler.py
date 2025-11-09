"""
Maintenance Scheduler Service for Energy Grid
Handles predictive maintenance and scheduling.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from neo4j import Driver

from ..repositories.incident_repo import IncidentRepository
from ..repositories.infrastructure_repo import InfrastructureRepository
from ..repositories.sensor_repo import SensorRepository


class MaintenanceSchedulerService:
    """Service for scheduling and managing maintenance activities."""
    
    def __init__(self, driver: Driver):
        """Initialize with Neo4j driver."""
        self.driver = driver
    
    def get_maintenance_priorities(self) -> Dict[str, Any]:
        """Get prioritized list of components needing maintenance."""
        with self.driver.session() as session:
            query = """
            // Power plants needing maintenance
            MATCH (pp:PowerPlant)
            OPTIONAL MATCH (pp)<-[:AFFECTS]-(i:Incident)
            WHERE i.reported_at >= datetime() - duration({days: 365})
            WITH pp, count(i) as incident_count
            
            OPTIONAL MATCH (pp)<-[:MONITORS]-(s:Sensor)
            WITH pp, incident_count, 
                 count(CASE WHEN s.status = 'faulty' THEN 1 END) as faulty_sensors
            
            RETURN 
                'PowerPlant' as component_type,
                pp.id as component_id,
                pp.name as component_name,
                pp.status as status,
                pp.capacity_mw as capacity,
                incident_count,
                faulty_sensors,
                (incident_count * 10 + faulty_sensors * 5) as priority_score
            
            UNION
            
            // Substations needing maintenance
            MATCH (ss:Substation)
            OPTIONAL MATCH (ss)<-[:AFFECTS]-(i:Incident)
            WHERE i.reported_at >= datetime() - duration({days: 365})
            WITH ss, count(i) as incident_count
            
            OPTIONAL MATCH (ss)<-[:MONITORS]-(s:Sensor)
            WITH ss, incident_count,
                 count(CASE WHEN s.status = 'faulty' THEN 1 END) as faulty_sensors
            
            OPTIONAL MATCH (ss)-[:SUPPLIES_TO]->(c:Customer)
            WITH ss, incident_count, faulty_sensors, count(c) as customer_count
            
            RETURN 
                'Substation' as component_type,
                ss.id as component_id,
                ss.name as component_name,
                ss.status as status,
                ss.capacity_mva as capacity,
                incident_count,
                faulty_sensors,
                (incident_count * 10 + faulty_sensors * 5 + customer_count * 2) as priority_score
            
            UNION
            
            // Transmission lines needing maintenance
            MATCH (tl:TransmissionLine)
            OPTIONAL MATCH (tl)<-[:AFFECTS]-(i:Incident)
            WHERE i.reported_at >= datetime() - duration({days: 365})
            WITH tl, count(i) as incident_count
            
            RETURN 
                'TransmissionLine' as component_type,
                tl.id as component_id,
                tl.name as component_name,
                tl.status as status,
                tl.capacity_mw as capacity,
                incident_count,
                0 as faulty_sensors,
                (incident_count * 10 + CASE WHEN tl.loss_percent > 5 THEN 20 ELSE 0 END) as priority_score
            
            ORDER BY priority_score DESC
            LIMIT 20
            """
            
            result = session.run(query)
            return [dict(record) for record in result]
    
    def schedule_preventive_maintenance(
        self,
        component_id: str,
        component_type: str,
        maintenance_type: str,
        scheduled_date: datetime,
        duration_hours: int,
        notes: Optional[str] = None
    ) -> str:
        """Schedule preventive maintenance."""
        with self.driver.session() as session:
            maintenance_id = f"MAINT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            query = f"""
            MATCH (component:{component_type} {{id: $component_id}})
            CREATE (m:Maintenance {{
                maintenance_id: $maintenance_id,
                type: $maintenance_type,
                scheduled_date: datetime($scheduled_date),
                duration_hours: $duration_hours,
                status: 'scheduled',
                notes: $notes,
                created_at: datetime()
            }})
            CREATE (m)-[:SCHEDULED_FOR]->(component)
            RETURN m.maintenance_id as maintenance_id
            """
            
            result = session.run(
                query,
                component_id=component_id,
                maintenance_id=maintenance_id,
                maintenance_type=maintenance_type,
                scheduled_date=scheduled_date.isoformat(),
                duration_hours=duration_hours,
                notes=notes
            )
            
            record = result.single()
            return record["maintenance_id"] if record else ""
    
    def get_maintenance_calendar(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get maintenance calendar for date range."""
        if not start_date:
            start_date = datetime.now()
        if not end_date:
            end_date = start_date + timedelta(days=30)
        
        with self.driver.session() as session:
            query = """
            MATCH (m:Maintenance)-[:SCHEDULED_FOR]->(component)
            WHERE m.scheduled_date >= datetime($start_date)
              AND m.scheduled_date <= datetime($end_date)
            OPTIONAL MATCH (component)-[:LOCATED_IN]->(l:Location)
            
            RETURN 
                m.maintenance_id as maintenance_id,
                m.type as maintenance_type,
                m.scheduled_date as scheduled_date,
                m.duration_hours as duration_hours,
                m.status as status,
                m.notes as notes,
                labels(component)[0] as component_type,
                component.id as component_id,
                component.name as component_name,
                l.name as location
            ORDER BY m.scheduled_date ASC
            """
            
            result = session.run(
                query,
                start_date=start_date.isoformat(),
                end_date=end_date.isoformat()
            )
            return [dict(record) for record in result]
    
    def identify_high_risk_components(self) -> List[Dict[str, Any]]:
        """Identify components at high risk of failure."""
        with self.driver.session() as session:
            query = """
            // Calculate risk scores based on multiple factors
            MATCH (component)
            WHERE component:PowerPlant OR component:Substation OR component:TransmissionLine
            
            // Count recent incidents
            OPTIONAL MATCH (component)<-[:AFFECTS]-(i:Incident)
            WHERE i.reported_at >= datetime() - duration({days: 180})
            WITH component, count(i) as recent_incidents
            
            // Count active sensors in alarm
            OPTIONAL MATCH (component)<-[:MONITORS]-(s:Sensor)
            WHERE s.status = 'active' 
              AND (s.current_value < s.threshold_min OR s.current_value > s.threshold_max)
            WITH component, recent_incidents, count(s) as alarms
            
            // Count faulty sensors
            OPTIONAL MATCH (component)<-[:MONITORS]-(fs:Sensor {status: 'faulty'})
            WITH component, recent_incidents, alarms, count(fs) as faulty_sensors
            
            // Check for maintenance
            OPTIONAL MATCH (m:Maintenance)-[:SCHEDULED_FOR]->(component)
            WHERE m.status = 'scheduled' AND m.scheduled_date > datetime()
            WITH component, recent_incidents, alarms, faulty_sensors,
                 count(m) as upcoming_maintenance
            
            // Calculate risk score
            WITH component, recent_incidents, alarms, faulty_sensors, upcoming_maintenance,
                 (recent_incidents * 20 + 
                  alarms * 15 + 
                  faulty_sensors * 10 -
                  upcoming_maintenance * 5) as risk_score
            
            WHERE risk_score > 20
            
            OPTIONAL MATCH (component)-[:LOCATED_IN]->(l:Location)
            
            RETURN 
                labels(component)[0] as component_type,
                component.id as component_id,
                component.name as component_name,
                component.status as status,
                l.name as location,
                recent_incidents,
                alarms,
                faulty_sensors,
                upcoming_maintenance,
                risk_score,
                CASE 
                    WHEN risk_score > 60 THEN 'CRITICAL'
                    WHEN risk_score > 40 THEN 'HIGH'
                    ELSE 'MEDIUM'
                END as risk_level
            ORDER BY risk_score DESC
            """
            
            result = session.run(query)
            return [dict(record) for record in result]
    
    def assess_maintenance_impact(
        self,
        component_id: str,
        component_type: str
    ) -> Dict[str, Any]:
        """Assess impact of taking component offline for maintenance."""
        with self.driver.session() as session:
            query = f"""
            MATCH (component:{component_type} {{id: $component_id}})
            OPTIONAL MATCH (component)-[:LOCATED_IN]->(l:Location)
            
            // Find directly connected customers
            OPTIONAL MATCH (component)-[:SUPPLIES_TO]->(c:Customer)
            WITH component, l, collect(c) as direct_customers
            
            // Find indirectly affected customers
            OPTIONAL MATCH path = (component)-[:CONNECTED_TO*1..3]->(ss:Substation)-[:SUPPLIES_TO]->(ic:Customer)
            WITH component, l, direct_customers, collect(DISTINCT ic) as indirect_customers
            
            WITH component, l, direct_customers, indirect_customers,
                 direct_customers + [c IN indirect_customers WHERE NOT c IN direct_customers] as all_customers
            
            RETURN 
                component.id as component_id,
                component.name as component_name,
                labels(component)[0] as component_type,
                component.status as current_status,
                l.name as location,
                size(direct_customers) as directly_affected_customers,
                size(all_customers) as total_affected_customers,
                reduce(load = 0.0, c IN all_customers | load + c.consumption_mw) as total_affected_load_mw,
                [c IN all_customers | {{
                    id: c.id,
                    name: c.name,
                    type: c.type,
                    consumption_mw: c.consumption_mw
                }}] as affected_customer_list
            """
            
            result = session.run(query, component_id=component_id)
            record = result.single()
            return dict(record) if record else {}
    
    def optimize_maintenance_schedule(self) -> List[Dict[str, Any]]:
        """Suggest optimal maintenance schedule to minimize impact."""
        with self.driver.session() as session:
            # Get components needing maintenance
            priorities = self.get_maintenance_priorities()
            
            optimized_schedule = []
            
            for priority in priorities[:10]:  # Top 10 priorities
                # Assess impact
                impact = self.assess_maintenance_impact(
                    priority["component_id"],
                    priority["component_type"]
                )
                
                # Suggest optimal time (e.g., lowest load period)
                suggested_date = datetime.now() + timedelta(days=7)  # Next week
                
                # Check for conflicts
                conflicts = self.check_maintenance_conflicts(
                    priority["component_id"],
                    priority["component_type"],
                    suggested_date,
                    duration_hours=8
                )
                
                optimized_schedule.append({
                    "component": priority,
                    "impact": impact,
                    "suggested_date": suggested_date.isoformat(),
                    "suggested_duration_hours": 8,
                    "has_conflicts": len(conflicts) > 0,
                    "conflicts": conflicts
                })
            
            return optimized_schedule
    
    def check_maintenance_conflicts(
        self,
        component_id: str,
        component_type: str,
        proposed_date: datetime,
        duration_hours: int
    ) -> List[Dict[str, Any]]:
        """Check for maintenance scheduling conflicts."""
        with self.driver.session() as session:
            end_time = proposed_date + timedelta(hours=duration_hours)
            
            query = f"""
            MATCH (component:{component_type} {{id: $component_id}})
            
            // Find nearby components
            MATCH (nearby)
            WHERE (component)-[:CONNECTED_TO]-(nearby) 
               OR (component)-[:LOCATED_IN]->()<-[:LOCATED_IN]-(nearby)
            
            // Check their maintenance schedules
            MATCH (m:Maintenance)-[:SCHEDULED_FOR]->(nearby)
            WHERE m.status = 'scheduled'
              AND m.scheduled_date <= datetime($end_time)
              AND datetime({{
                  year: m.scheduled_date.year,
                  month: m.scheduled_date.month,
                  day: m.scheduled_date.day,
                  hour: m.scheduled_date.hour + m.duration_hours
              }}) >= datetime($proposed_date)
            
            RETURN 
                nearby.id as conflicting_component_id,
                nearby.name as conflicting_component_name,
                labels(nearby)[0] as conflicting_component_type,
                m.maintenance_id as maintenance_id,
                m.scheduled_date as scheduled_date,
                m.duration_hours as duration_hours
            """
            
            result = session.run(
                query,
                component_id=component_id,
                proposed_date=proposed_date.isoformat(),
                end_time=end_time.isoformat()
            )
            return [dict(record) for record in result]
    
    def get_maintenance_recommendations(self) -> Dict[str, Any]:
        """Get comprehensive maintenance recommendations."""
        priorities = self.get_maintenance_priorities()
        high_risk = self.identify_high_risk_components()
        optimized = self.optimize_maintenance_schedule()
        
        return {
            "priorities": priorities,
            "high_risk_components": high_risk,
            "optimized_schedule": optimized,
            "summary": {
                "components_needing_maintenance": len(priorities),
                "high_risk_count": len(high_risk),
                "recommended_immediate_action": len([c for c in high_risk if c["risk_level"] == "CRITICAL"])
            }
        }
