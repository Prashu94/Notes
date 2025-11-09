"""Repository for incident and service request operations."""

from typing import List, Dict, Any, Optional
from datetime import datetime

from ..connection import Neo4jConnection
from ..models.incident import Incident, IncidentType, IncidentSeverity, IncidentStatus
from ..models.service_request import ServiceRequest, RequestType, RequestStatus, RequestPriority


class IncidentRepository:
    """Repository for managing incidents and service requests."""
    
    def __init__(self):
        """Initialize repository with database connection."""
        self.conn = Neo4jConnection()
    
    # Incident operations
    def create_incident(self, incident: Incident) -> str:
        """Create a new incident."""
        query = """
        CREATE (i:Incident $props)
        RETURN i.id as id
        """
        result = self.conn.execute_query(query, props=incident.to_neo4j_properties())
        return result[0]['id'] if result else None
    
    def get_incident(self, incident_id: str) -> Optional[Dict[str, Any]]:
        """Get incident by ID."""
        query = """
        MATCH (i:Incident {id: $incident_id})
        RETURN i
        """
        result = self.conn.execute_query(query, incident_id=incident_id)
        return dict(result[0]['i']) if result else None
    
    def update_incident(self, incident_id: str, updates: Dict[str, Any]) -> bool:
        """Update incident properties."""
        query = """
        MATCH (i:Incident {id: $incident_id})
        SET i += $updates
        RETURN i.id as id
        """
        result = self.conn.execute_query(query, incident_id=incident_id, updates=updates)
        return len(result) > 0
    
    def update_incident_status(
        self,
        incident_id: str,
        new_status: str,
        notes: Optional[str] = None
    ) -> bool:
        """Update incident status."""
        updates = {'status': new_status}
        
        if new_status == 'confirmed' and notes:
            updates['confirmed_date'] = datetime.now().isoformat()
        elif new_status in ['resolved', 'closed']:
            updates['resolved_date'] = datetime.now().isoformat()
            if notes:
                updates['resolution_notes'] = notes
        
        return self.update_incident(incident_id, updates)
    
    def get_active_incidents(self) -> List[Dict[str, Any]]:
        """Get all active (not resolved/closed) incidents."""
        query = """
        MATCH (i:Incident)
        WHERE i.status NOT IN ['resolved', 'closed']
        RETURN i,
               duration.between(datetime(i.reported_date), datetime()).hours as hours_active
        ORDER BY i.severity DESC, hours_active DESC
        """
        result = self.conn.execute_query(query)
        return result
    
    def get_incidents_by_type(self, incident_type: str) -> List[Dict[str, Any]]:
        """Get incidents by type."""
        query = """
        MATCH (i:Incident {type: $incident_type})
        RETURN i
        ORDER BY i.reported_date DESC
        LIMIT 100
        """
        result = self.conn.execute_query(query, incident_type=incident_type)
        return [dict(r['i']) for r in result]
    
    def get_incidents_by_severity(self, severity: str) -> List[Dict[str, Any]]:
        """Get incidents by severity."""
        query = """
        MATCH (i:Incident {severity: $severity})
        WHERE i.status NOT IN ['resolved', 'closed']
        RETURN i
        ORDER BY i.reported_date DESC
        """
        result = self.conn.execute_query(query, severity=severity)
        return [dict(r['i']) for r in result]
    
    def get_critical_incidents(self) -> List[Dict[str, Any]]:
        """Get all critical incidents."""
        return self.get_incidents_by_severity('critical')
    
    def link_incident_to_infrastructure(
        self,
        incident_id: str,
        infrastructure_id: str,
        infrastructure_type: str = "PipelineSegment"
    ) -> bool:
        """Link incident to affected infrastructure."""
        query = f"""
        MATCH (i:Incident {{id: $incident_id}})
        MATCH (infra:{infrastructure_type} {{id: $infrastructure_id}})
        MERGE (i)-[r:AFFECTS]->(infra)
        RETURN i.id as incident_id, infra.id as infrastructure_id
        """
        result = self.conn.execute_query(
            query,
            incident_id=incident_id,
            infrastructure_id=infrastructure_id
        )
        return len(result) > 0
    
    def link_incident_to_customer(self, incident_id: str, customer_id: str) -> bool:
        """Link incident to affected customer."""
        query = """
        MATCH (i:Incident {id: $incident_id})
        MATCH (c:Customer {id: $customer_id})
        MERGE (i)-[r:AFFECTS]->(c)
        RETURN i.id as incident_id, c.id as customer_id
        """
        result = self.conn.execute_query(
            query,
            incident_id=incident_id,
            customer_id=customer_id
        )
        return len(result) > 0
    
    def get_incident_affected_customers(self, incident_id: str) -> List[Dict[str, Any]]:
        """Get customers affected by an incident."""
        query = """
        MATCH (i:Incident {id: $incident_id})-[:AFFECTS]->(c:Customer)
        RETURN c
        ORDER BY c.name
        """
        result = self.conn.execute_query(query, incident_id=incident_id)
        return [dict(r['c']) for r in result]
    
    def get_incident_affected_infrastructure(self, incident_id: str) -> List[Dict[str, Any]]:
        """Get infrastructure affected by an incident."""
        query = """
        MATCH (i:Incident {id: $incident_id})-[:AFFECTS]->(infra)
        WHERE infra:PipelineSegment OR infra:Meter OR infra:StorageTank
        RETURN labels(infra)[0] as type, infra
        """
        result = self.conn.execute_query(query, incident_id=incident_id)
        return result
    
    def get_incidents_by_location(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 5.0
    ) -> List[Dict[str, Any]]:
        """Get incidents near a location (requires geospatial index)."""
        query = """
        MATCH (i:Incident)
        WHERE i.latitude IS NOT NULL
          AND i.longitude IS NOT NULL
          AND point.distance(
              point({latitude: i.latitude, longitude: i.longitude}),
              point({latitude: $lat, longitude: $lon})
          ) <= $radius * 1000
        WITH i,
             point.distance(
                 point({latitude: i.latitude, longitude: i.longitude}),
                 point({latitude: $lat, longitude: $lon})
             ) / 1000.0 as distance_km
        RETURN i, round(distance_km, 2) as distance_km
        ORDER BY distance_km
        """
        result = self.conn.execute_query(
            query,
            lat=latitude,
            lon=longitude,
            radius=radius_km
        )
        return result
    
    # Service Request operations
    def create_service_request(self, request: ServiceRequest) -> str:
        """Create a new service request."""
        query = """
        CREATE (sr:ServiceRequest $props)
        RETURN sr.id as id
        """
        result = self.conn.execute_query(query, props=request.to_neo4j_properties())
        return result[0]['id'] if result else None
    
    def get_service_request(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Get service request by ID."""
        query = """
        MATCH (sr:ServiceRequest {id: $request_id})
        RETURN sr
        """
        result = self.conn.execute_query(query, request_id=request_id)
        return dict(result[0]['sr']) if result else None
    
    def update_service_request(self, request_id: str, updates: Dict[str, Any]) -> bool:
        """Update service request properties."""
        query = """
        MATCH (sr:ServiceRequest {id: $request_id})
        SET sr += $updates
        RETURN sr.id as id
        """
        result = self.conn.execute_query(query, request_id=request_id, updates=updates)
        return len(result) > 0
    
    def assign_service_request(
        self,
        request_id: str,
        assigned_to: str,
        scheduled_date: Optional[datetime] = None
    ) -> bool:
        """Assign service request to a technician/team."""
        updates = {
            'assigned_to': assigned_to,
            'assigned_date': datetime.now().isoformat(),
            'status': 'assigned'
        }
        if scheduled_date:
            updates['scheduled_date'] = scheduled_date.isoformat()
        
        return self.update_service_request(request_id, updates)
    
    def complete_service_request(
        self,
        request_id: str,
        resolution_notes: str,
        actual_duration_hours: Optional[float] = None
    ) -> bool:
        """Mark service request as completed."""
        updates = {
            'status': 'resolved',
            'completed_date': datetime.now().isoformat(),
            'resolution_notes': resolution_notes
        }
        if actual_duration_hours is not None:
            updates['actual_duration_hours'] = actual_duration_hours
        
        return self.update_service_request(request_id, updates)
    
    def get_pending_service_requests(self) -> List[Dict[str, Any]]:
        """Get all pending (unassigned) service requests."""
        query = """
        MATCH (sr:ServiceRequest {status: 'pending'})
        WITH sr,
             duration.between(datetime(sr.created_date), datetime()).hours as age_hours
        RETURN sr, age_hours
        ORDER BY sr.priority DESC, age_hours DESC
        """
        result = self.conn.execute_query(query)
        return result
    
    def get_service_requests_by_priority(self, priority: str) -> List[Dict[str, Any]]:
        """Get service requests by priority."""
        query = """
        MATCH (sr:ServiceRequest {priority: $priority})
        WHERE sr.status NOT IN ['resolved', 'closed', 'cancelled']
        RETURN sr
        ORDER BY sr.created_date
        """
        result = self.conn.execute_query(query, priority=priority)
        return [dict(r['sr']) for r in result]
    
    def get_customer_service_requests(
        self,
        customer_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get service requests for a customer."""
        query = """
        MATCH (sr:ServiceRequest {customer_id: $customer_id})
        RETURN sr
        ORDER BY sr.created_date DESC
        LIMIT $limit
        """
        result = self.conn.execute_query(query, customer_id=customer_id, limit=limit)
        return [dict(r['sr']) for r in result]
    
    def get_overdue_service_requests(self) -> List[Dict[str, Any]]:
        """Get service requests that are overdue based on SLA."""
        query = """
        MATCH (sr:ServiceRequest)
        WHERE sr.status NOT IN ['resolved', 'closed', 'cancelled']
        WITH sr,
             duration.between(datetime(sr.created_date), datetime()).hours as age_hours,
             CASE sr.priority
                WHEN 'critical' THEN 2
                WHEN 'high' THEN 24
                WHEN 'medium' THEN 72
                ELSE 168
             END as sla_hours
        WHERE age_hours > sla_hours
        RETURN sr, age_hours, sla_hours, (age_hours - sla_hours) as hours_overdue
        ORDER BY hours_overdue DESC
        """
        result = self.conn.execute_query(query)
        return result
    
    def link_service_request_to_incident(self, request_id: str, incident_id: str) -> bool:
        """Link service request to related incident."""
        query = """
        MATCH (sr:ServiceRequest {id: $request_id})
        MATCH (i:Incident {id: $incident_id})
        MERGE (sr)-[r:RELATED_TO]->(i)
        SET sr.related_incident_id = i.id
        RETURN sr.id as request_id, i.id as incident_id
        """
        result = self.conn.execute_query(query, request_id=request_id, incident_id=incident_id)
        return len(result) > 0
    
    # Analytics
    def get_incident_statistics(self, days: int = 30) -> Dict[str, Any]:
        """Get incident statistics for a time period."""
        query = """
        MATCH (i:Incident)
        WHERE date(i.reported_date) >= date() - duration({days: $days})
        WITH count(i) as total_incidents,
             count(CASE WHEN i.status IN ['resolved', 'closed'] THEN 1 END) as resolved,
             count(CASE WHEN i.severity = 'critical' THEN 1 END) as critical,
             count(CASE WHEN i.severity = 'high' THEN 1 END) as high,
             sum(i.customers_affected) as total_customers_affected
        MATCH (i:Incident)
        WHERE date(i.reported_date) >= date() - duration({days: $days})
          AND i.resolved_date IS NOT NULL
        WITH total_incidents, resolved, critical, high, total_customers_affected,
             avg(duration.between(datetime(i.reported_date), datetime(i.resolved_date)).hours) as avg_resolution_hours
        RETURN total_incidents,
               resolved,
               critical,
               high,
               total_customers_affected,
               round(avg_resolution_hours, 1) as avg_resolution_hours,
               round((toFloat(resolved) / total_incidents) * 100, 1) as resolution_rate_percent
        """
        result = self.conn.execute_query(query, days=days)
        return result[0] if result else {}
    
    def get_incident_trend(self, months: int = 12) -> List[Dict[str, Any]]:
        """Get incident trend over time."""
        query = """
        MATCH (i:Incident)
        WHERE date(i.reported_date) >= date() - duration({months: $months})
        WITH date.truncate('month', date(i.reported_date)) as month,
             count(i) as incident_count,
             collect(DISTINCT i.type) as types
        RETURN toString(month) as month,
               incident_count,
               types
        ORDER BY month DESC
        """
        result = self.conn.execute_query(query, months=months)
        return result
    
    def get_service_request_statistics(self, days: int = 30) -> Dict[str, Any]:
        """Get service request statistics."""
        query = """
        MATCH (sr:ServiceRequest)
        WHERE date(sr.created_date) >= date() - duration({days: $days})
        WITH count(sr) as total_requests,
             count(CASE WHEN sr.status IN ['resolved', 'closed'] THEN 1 END) as resolved,
             count(CASE WHEN sr.priority = 'critical' THEN 1 END) as critical,
             count(CASE WHEN sr.priority = 'high' THEN 1 END) as high
        MATCH (sr:ServiceRequest)
        WHERE date(sr.created_date) >= date() - duration({days: $days})
          AND sr.completed_date IS NOT NULL
        WITH total_requests, resolved, critical, high,
             avg(duration.between(datetime(sr.created_date), datetime(sr.completed_date)).hours) as avg_resolution_hours,
             avg(sr.customer_satisfaction) as avg_satisfaction
        RETURN total_requests,
               resolved,
               critical,
               high,
               round(avg_resolution_hours, 1) as avg_resolution_hours,
               round(avg_satisfaction, 1) as avg_customer_satisfaction,
               round((toFloat(resolved) / total_requests) * 100, 1) as resolution_rate_percent
        """
        result = self.conn.execute_query(query, days=days)
        return result[0] if result else {}
    
    def get_most_common_issues(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most common service request types."""
        query = """
        MATCH (sr:ServiceRequest)
        WHERE date(sr.created_date) >= date() - duration({months: 3})
        WITH sr.type as issue_type,
             count(sr) as count,
             avg(CASE WHEN sr.completed_date IS NOT NULL
                 THEN duration.between(datetime(sr.created_date), datetime(sr.completed_date)).hours
                 ELSE null END) as avg_resolution_hours
        RETURN issue_type,
               count,
               round(avg_resolution_hours, 1) as avg_resolution_hours
        ORDER BY count DESC
        LIMIT $limit
        """
        result = self.conn.execute_query(query, limit=limit)
        return result
