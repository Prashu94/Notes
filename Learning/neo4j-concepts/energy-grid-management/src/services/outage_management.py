"""
Outage Management Service for Energy Grid
Handles incident response, tracking, and resolution.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from neo4j import Driver

from ..models.incident import Incident, IncidentType, IncidentSeverity, IncidentStatus
from ..repositories.incident_repo import IncidentRepository
from ..repositories.infrastructure_repo import InfrastructureRepository


class OutageManagementService:
    """Service for managing grid outages and incidents."""
    
    def __init__(self, driver: Driver):
        """Initialize with Neo4j driver."""
        self.driver = driver
    
    def report_incident(
        self,
        incident_type: IncidentType,
        severity: IncidentSeverity,
        description: str,
        affected_component_id: str,
        affected_component_type: str,
        affected_customers: int = 0,
        power_loss_mw: float = 0.0
    ) -> str:
        """Report a new incident."""
        incident = Incident(
            incident_id=f"INC-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            type=incident_type,
            severity=severity,
            status=IncidentStatus.REPORTED,
            description=description,
            reported_at=datetime.now(),
            affected_customers=affected_customers,
            power_loss_mw=power_loss_mw
        )
        
        with self.driver.session() as session:
            repo = IncidentRepository(session)
            incident_id = repo.create_incident(incident)
            repo.link_incident_to_component(
                incident_id, 
                affected_component_id, 
                affected_component_type
            )
        
        return incident_id
    
    def get_active_outages(self) -> List[Dict[str, Any]]:
        """Get all active outages with affected components."""
        with self.driver.session() as session:
            query = """
            MATCH (i:Incident)-[:AFFECTS]->(component)
            WHERE i.status IN ['reported', 'investigating', 'in_progress']
            OPTIONAL MATCH (component)-[:LOCATED_IN]->(l:Location)
            RETURN 
                i.incident_id as incident_id,
                i.type as incident_type,
                i.severity as severity,
                i.status as status,
                i.description as description,
                i.reported_at as reported_at,
                i.affected_customers as affected_customers,
                i.power_loss_mw as power_loss_mw,
                labels(component)[0] as component_type,
                component.id as component_id,
                component.name as component_name,
                l.name as location
            ORDER BY 
                CASE i.severity
                    WHEN 'critical' THEN 1
                    WHEN 'high' THEN 2
                    WHEN 'medium' THEN 3
                    ELSE 4
                END,
                i.reported_at ASC
            """
            
            result = session.run(query)
            return [dict(record) for record in result]
    
    def get_outage_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive outage dashboard."""
        with self.driver.session() as session:
            incident_repo = IncidentRepository(session)
            
            # Get statistics
            stats = incident_repo.get_incident_statistics()
            
            # Get active incidents
            active = incident_repo.get_active_incidents()
            
            # Get critical incidents
            critical = incident_repo.get_critical_incidents()
            
            # Get incident trends
            trends = incident_repo.get_incident_trend(days=7)
            
            # Get affected components
            affected_components = incident_repo.get_most_affected_components(limit=5)
        
        return {
            "statistics": stats,
            "active_incidents": [
                {
                    "incident_id": inc.incident_id,
                    "type": inc.type.value,
                    "severity": inc.severity.value,
                    "status": inc.status.value,
                    "description": inc.description,
                    "affected_customers": inc.affected_customers,
                    "power_loss_mw": inc.power_loss_mw,
                    "duration_minutes": inc.duration_minutes
                }
                for inc in active
            ],
            "critical_incidents": [
                {
                    "incident_id": inc.incident_id,
                    "type": inc.type.value,
                    "description": inc.description,
                    "reported_at": inc.reported_at.isoformat()
                }
                for inc in critical
            ],
            "weekly_trend": trends,
            "most_affected_components": affected_components
        }
    
    def update_incident_status(
        self,
        incident_id: str,
        new_status: IncidentStatus,
        resolution_notes: Optional[str] = None
    ) -> bool:
        """Update incident status with notes."""
        with self.driver.session() as session:
            repo = IncidentRepository(session)
            return repo.update_incident_status(incident_id, new_status, resolution_notes)
    
    def resolve_incident(
        self,
        incident_id: str,
        root_cause: str,
        resolution_notes: str,
        estimated_cost: Optional[float] = None
    ) -> bool:
        """Mark incident as resolved with details."""
        with self.driver.session() as session:
            repo = IncidentRepository(session)
            
            # Get incident
            incident = repo.get_incident_by_id(incident_id)
            if not incident:
                return False
            
            # Update incident
            incident.status = IncidentStatus.RESOLVED
            incident.resolved_at = datetime.now()
            incident.root_cause = root_cause
            incident.resolution_notes = resolution_notes
            if estimated_cost:
                incident.estimated_cost = estimated_cost
            
            return repo.update_incident(incident)
    
    def get_incident_impact(self, incident_id: str) -> Dict[str, Any]:
        """Analyze the full impact of an incident."""
        with self.driver.session() as session:
            query = """
            MATCH (i:Incident {incident_id: $incident_id})-[:AFFECTS]->(component)
            OPTIONAL MATCH (component)-[:LOCATED_IN]->(l:Location)
            
            // Find downstream affected customers
            OPTIONAL MATCH path = (component)-[:SUPPLIES_TO|CONNECTED_TO*1..3]->(c:Customer)
            WITH i, component, l, collect(DISTINCT c) as affected_customers
            
            // Calculate impact
            RETURN 
                i.incident_id as incident_id,
                i.type as incident_type,
                i.severity as severity,
                i.description as description,
                i.reported_at as reported_at,
                labels(component)[0] as affected_component_type,
                component.id as affected_component_id,
                component.name as affected_component_name,
                l.name as location,
                size(affected_customers) as downstream_customers,
                [c IN affected_customers | {
                    id: c.id,
                    name: c.name,
                    type: c.type,
                    consumption_mw: c.consumption_mw
                }] as customer_list,
                reduce(total = 0.0, c IN affected_customers | total + c.consumption_mw) as total_affected_consumption_mw
            """
            
            result = session.run(query, incident_id=incident_id)
            record = result.single()
            return dict(record) if record else {}
    
    def find_alternative_power_paths(
        self,
        affected_component_id: str,
        affected_component_type: str
    ) -> List[Dict[str, Any]]:
        """Find alternative power delivery paths during outage."""
        with self.driver.session() as session:
            query = f"""
            // Find affected customers
            MATCH (affected:{affected_component_type} {{id: $component_id}})
            MATCH (affected)-[:SUPPLIES_TO|CONNECTED_TO*1..2]->(c:Customer)
            
            // Find alternative substations that could supply these customers
            MATCH (alternative:Substation)
            WHERE alternative.id <> $component_id
              AND alternative.status = 'operational'
            
            // Check if there's a path
            MATCH path = shortestPath((alternative)-[:CONNECTED_TO*..5]-(affected))
            WHERE NONE(r IN relationships(path) WHERE r.status = 'inactive')
            
            WITH c, alternative, path,
                 reduce(dist = 0, r IN relationships(path) | dist + 1) as hop_count
            
            RETURN 
                c.id as customer_id,
                c.name as customer_name,
                c.consumption_mw as consumption_mw,
                alternative.id as alternative_substation_id,
                alternative.name as alternative_substation_name,
                alternative.capacity_mva as available_capacity,
                hop_count,
                [node IN nodes(path) | {{id: node.id, name: node.name}}] as path_nodes
            ORDER BY c.consumption_mw DESC, hop_count ASC
            LIMIT 20
            """
            
            result = session.run(query, component_id=affected_component_id)
            return [dict(record) for record in result]
    
    def get_mttr_statistics(self) -> Dict[str, Any]:
        """Get Mean Time To Resolution statistics."""
        with self.driver.session() as session:
            repo = IncidentRepository(session)
            return repo.get_mttr_by_type()
    
    def predict_restoration_time(self, incident_id: str) -> Dict[str, Any]:
        """Predict restoration time based on historical data."""
        with self.driver.session() as session:
            repo = IncidentRepository(session)
            
            # Get current incident
            incident = repo.get_incident_by_id(incident_id)
            if not incident:
                return {}
            
            # Get historical MTTR for this incident type
            mttr_stats = repo.get_mttr_by_type()
            
            # Find matching incident type
            historical_mttr = None
            for stat in mttr_stats:
                if stat["incident_type"] == incident.type.value:
                    historical_mttr = stat["avg_resolution_minutes"]
                    break
            
            if not historical_mttr:
                historical_mttr = 180  # Default 3 hours
            
            # Adjust based on severity
            severity_multiplier = {
                IncidentSeverity.CRITICAL: 1.5,
                IncidentSeverity.HIGH: 1.2,
                IncidentSeverity.MEDIUM: 1.0,
                IncidentSeverity.LOW: 0.8
            }
            
            multiplier = severity_multiplier.get(incident.severity, 1.0)
            estimated_minutes = historical_mttr * multiplier
            estimated_completion = incident.reported_at + timedelta(minutes=estimated_minutes)
            
            return {
                "incident_id": incident_id,
                "incident_type": incident.type.value,
                "severity": incident.severity.value,
                "reported_at": incident.reported_at.isoformat(),
                "historical_avg_mttr_minutes": historical_mttr,
                "severity_multiplier": multiplier,
                "estimated_resolution_minutes": estimated_minutes,
                "estimated_completion_time": estimated_completion.isoformat(),
                "time_elapsed_minutes": incident.duration_minutes if incident.duration_minutes else 0
            }
