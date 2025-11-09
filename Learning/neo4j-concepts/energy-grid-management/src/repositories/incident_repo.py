"""
Incident Repository for Energy Grid Management
Handles database operations for incidents, outages, and faults.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from neo4j import Session

from ..models.incident import Incident, IncidentType, IncidentSeverity, IncidentStatus


class IncidentRepository:
    """Repository for incident-related database operations."""
    
    def __init__(self, session: Session):
        """Initialize with Neo4j session."""
        self.session = session
    
    # CREATE operations
    
    def create_incident(self, incident: Incident) -> str:
        """Create a new incident in the database."""
        query = """
        CREATE (i:Incident {
            incident_id: $incident_id,
            type: $type,
            severity: $severity,
            status: $status,
            description: $description,
            reported_at: datetime($reported_at),
            resolved_at: $resolved_at,
            affected_customers: $affected_customers,
            power_loss_mw: $power_loss_mw,
            estimated_cost: $estimated_cost,
            root_cause: $root_cause,
            resolution_notes: $resolution_notes
        })
        RETURN i.incident_id as incident_id
        """
        
        params = incident.to_neo4j_dict()
        result = self.session.run(query, **params)
        record = result.single()
        return record["incident_id"]
    
    def link_incident_to_component(
        self, 
        incident_id: str, 
        component_id: str, 
        component_type: str
    ) -> None:
        """Link incident to affected component (PowerPlant, Substation, TransmissionLine)."""
        query = f"""
        MATCH (i:Incident {{incident_id: $incident_id}})
        MATCH (c:{component_type} {{id: $component_id}})
        CREATE (i)-[:AFFECTS]->(c)
        """
        
        self.session.run(query, incident_id=incident_id, component_id=component_id)
    
    # READ operations
    
    def get_incident_by_id(self, incident_id: str) -> Optional[Incident]:
        """Get incident by ID."""
        query = """
        MATCH (i:Incident {incident_id: $incident_id})
        RETURN i
        """
        
        result = self.session.run(query, incident_id=incident_id)
        record = result.single()
        
        if not record:
            return None
        
        return Incident.from_neo4j_dict(dict(record["i"]))
    
    def get_all_incidents(self, limit: int = 100) -> List[Incident]:
        """Get all incidents."""
        query = """
        MATCH (i:Incident)
        RETURN i
        ORDER BY i.reported_at DESC
        LIMIT $limit
        """
        
        result = self.session.run(query, limit=limit)
        return [Incident.from_neo4j_dict(dict(record["i"])) for record in result]
    
    def get_active_incidents(self) -> List[Incident]:
        """Get all active incidents."""
        query = """
        MATCH (i:Incident)
        WHERE i.status IN ['reported', 'investigating', 'in_progress']
        RETURN i
        ORDER BY i.severity DESC, i.reported_at ASC
        """
        
        result = self.session.run(query)
        return [Incident.from_neo4j_dict(dict(record["i"])) for record in result]
    
    def get_critical_incidents(self) -> List[Incident]:
        """Get critical severity incidents."""
        query = """
        MATCH (i:Incident)
        WHERE i.severity = 'critical' AND i.status <> 'resolved'
        RETURN i
        ORDER BY i.reported_at ASC
        """
        
        result = self.session.run(query)
        return [Incident.from_neo4j_dict(dict(record["i"])) for record in result]
    
    def get_incidents_by_type(self, incident_type: IncidentType) -> List[Incident]:
        """Get incidents by type."""
        query = """
        MATCH (i:Incident {type: $type})
        RETURN i
        ORDER BY i.reported_at DESC
        LIMIT 100
        """
        
        result = self.session.run(query, type=incident_type.value)
        return [Incident.from_neo4j_dict(dict(record["i"])) for record in result]
    
    def get_incidents_by_component(
        self, 
        component_id: str, 
        component_type: str
    ) -> List[Incident]:
        """Get all incidents affecting a specific component."""
        query = f"""
        MATCH (i:Incident)-[:AFFECTS]->(c:{component_type} {{id: $component_id}})
        RETURN i
        ORDER BY i.reported_at DESC
        """
        
        result = self.session.run(query, component_id=component_id)
        return [Incident.from_neo4j_dict(dict(record["i"])) for record in result]
    
    def get_incidents_in_date_range(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[Incident]:
        """Get incidents reported within a date range."""
        query = """
        MATCH (i:Incident)
        WHERE i.reported_at >= datetime($start_date) 
          AND i.reported_at <= datetime($end_date)
        RETURN i
        ORDER BY i.reported_at DESC
        """
        
        result = self.session.run(
            query, 
            start_date=start_date.isoformat(), 
            end_date=end_date.isoformat()
        )
        return [Incident.from_neo4j_dict(dict(record["i"])) for record in result]
    
    # UPDATE operations
    
    def update_incident_status(
        self, 
        incident_id: str, 
        status: IncidentStatus,
        resolution_notes: Optional[str] = None
    ) -> bool:
        """Update incident status."""
        resolved_at = datetime.now().isoformat() if status == IncidentStatus.RESOLVED else None
        
        query = """
        MATCH (i:Incident {incident_id: $incident_id})
        SET i.status = $status
        """
        
        if resolved_at:
            query += ", i.resolved_at = datetime($resolved_at)"
        
        if resolution_notes:
            query += ", i.resolution_notes = $resolution_notes"
        
        query += " RETURN i"
        
        result = self.session.run(
            query,
            incident_id=incident_id,
            status=status.value,
            resolved_at=resolved_at,
            resolution_notes=resolution_notes
        )
        
        return result.single() is not None
    
    def update_incident(self, incident: Incident) -> bool:
        """Update entire incident record."""
        query = """
        MATCH (i:Incident {incident_id: $incident_id})
        SET i.type = $type,
            i.severity = $severity,
            i.status = $status,
            i.description = $description,
            i.affected_customers = $affected_customers,
            i.power_loss_mw = $power_loss_mw,
            i.estimated_cost = $estimated_cost,
            i.root_cause = $root_cause,
            i.resolution_notes = $resolution_notes
        RETURN i
        """
        
        params = incident.to_neo4j_dict()
        result = self.session.run(query, **params)
        return result.single() is not None
    
    # DELETE operations
    
    def delete_incident(self, incident_id: str) -> bool:
        """Delete an incident and its relationships."""
        query = """
        MATCH (i:Incident {incident_id: $incident_id})
        DETACH DELETE i
        RETURN count(i) as deleted
        """
        
        result = self.session.run(query, incident_id=incident_id)
        record = result.single()
        return record["deleted"] > 0
    
    # ANALYTICS operations
    
    def get_incident_statistics(self) -> Dict[str, Any]:
        """Get overall incident statistics."""
        query = """
        MATCH (i:Incident)
        WITH i
        RETURN 
            count(i) as total_incidents,
            count(CASE WHEN i.status IN ['reported', 'investigating', 'in_progress'] 
                  THEN 1 END) as active_incidents,
            count(CASE WHEN i.severity = 'critical' THEN 1 END) as critical_incidents,
            count(CASE WHEN i.status = 'resolved' THEN 1 END) as resolved_incidents,
            sum(i.affected_customers) as total_affected_customers,
            sum(i.power_loss_mw) as total_power_loss_mw,
            avg(i.power_loss_mw) as avg_power_loss_mw,
            sum(i.estimated_cost) as total_estimated_cost
        """
        
        result = self.session.run(query)
        record = result.single()
        return dict(record) if record else {}
    
    def get_incident_stats_by_type(self) -> List[Dict[str, Any]]:
        """Get incident statistics grouped by type."""
        query = """
        MATCH (i:Incident)
        WITH i.type as incident_type, i
        RETURN 
            incident_type,
            count(i) as count,
            count(CASE WHEN i.status IN ['reported', 'investigating', 'in_progress'] 
                  THEN 1 END) as active,
            count(CASE WHEN i.severity = 'critical' THEN 1 END) as critical,
            sum(i.affected_customers) as total_affected_customers,
            avg(i.power_loss_mw) as avg_power_loss_mw
        ORDER BY count DESC
        """
        
        result = self.session.run(query)
        return [dict(record) for record in result]
    
    def get_mttr_by_type(self) -> List[Dict[str, Any]]:
        """Get Mean Time To Resolution by incident type."""
        query = """
        MATCH (i:Incident)
        WHERE i.status = 'resolved' AND i.resolved_at IS NOT NULL
        WITH i.type as incident_type,
             duration.inSeconds(i.reported_at, i.resolved_at).minutes as resolution_minutes
        RETURN 
            incident_type,
            count(*) as resolved_count,
            avg(resolution_minutes) as avg_resolution_minutes,
            min(resolution_minutes) as min_resolution_minutes,
            max(resolution_minutes) as max_resolution_minutes
        ORDER BY avg_resolution_minutes DESC
        """
        
        result = self.session.run(query)
        return [dict(record) for record in result]
    
    def get_most_affected_components(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get components with most incidents."""
        query = """
        MATCH (i:Incident)-[:AFFECTS]->(c)
        WITH labels(c)[0] as component_type, 
             c.id as component_id,
             c.name as component_name,
             count(i) as incident_count,
             count(CASE WHEN i.status IN ['reported', 'investigating', 'in_progress'] 
                   THEN 1 END) as active_incidents
        RETURN component_type, component_id, component_name, 
               incident_count, active_incidents
        ORDER BY incident_count DESC
        LIMIT $limit
        """
        
        result = self.session.run(query, limit=limit)
        return [dict(record) for record in result]
    
    def get_incident_trend(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get incident trend over time."""
        query = """
        MATCH (i:Incident)
        WHERE i.reported_at >= datetime() - duration({days: $days})
        WITH date(i.reported_at) as incident_date, i
        RETURN 
            incident_date,
            count(i) as incident_count,
            count(CASE WHEN i.severity = 'critical' THEN 1 END) as critical_count,
            sum(i.affected_customers) as affected_customers,
            sum(i.power_loss_mw) as power_loss_mw
        ORDER BY incident_date DESC
        """
        
        result = self.session.run(query, days=days)
        return [dict(record) for record in result]
