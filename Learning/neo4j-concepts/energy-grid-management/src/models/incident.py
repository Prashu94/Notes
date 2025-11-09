"""
Incident Model

Data model for grid incidents, outages, and faults.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Literal, Dict, Any, Optional, List


IncidentType = Literal['outage', 'fault', 'overload', 'equipment_failure', 'weather', 'maintenance']
IncidentSeverity = Literal['low', 'medium', 'high', 'critical']
IncidentStatus = Literal['reported', 'investigating', 'in_progress', 'resolved', 'closed']


@dataclass
class Incident:
    """Model for grid incident nodes."""
    
    id: str
    type: IncidentType
    severity: IncidentSeverity
    status: IncidentStatus
    description: str
    reported_at: datetime
    location: Optional[str] = None
    affected_component_id: Optional[str] = None
    affected_component_type: Optional[str] = None
    cause: Optional[str] = None
    resolution: Optional[str] = None
    resolved_at: Optional[datetime] = None
    estimated_restoration: Optional[datetime] = None
    affected_customers: int = 0
    power_loss_mw: float = 0.0
    
    @property
    def is_active(self) -> bool:
        """Check if incident is still active."""
        return self.status not in ['resolved', 'closed']
    
    @property
    def is_critical(self) -> bool:
        """Check if incident is critical."""
        return self.severity == 'critical'
    
    @property
    def duration_minutes(self) -> Optional[float]:
        """Calculate incident duration in minutes."""
        if self.resolved_at:
            delta = self.resolved_at - self.reported_at
            return delta.total_seconds() / 60
        return None
    
    @property
    def is_major_outage(self, customer_threshold: int = 1000) -> bool:
        """Check if this is a major outage."""
        return self.type == 'outage' and self.affected_customers >= customer_threshold
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Neo4j."""
        data = {
            'id': self.id,
            'type': self.type,
            'severity': self.severity,
            'status': self.status,
            'description': self.description,
            'reported_at': self.reported_at.isoformat(),
            'affected_customers': self.affected_customers,
            'power_loss_mw': self.power_loss_mw,
        }
        
        if self.location:
            data['location'] = self.location
        if self.affected_component_id:
            data['affected_component_id'] = self.affected_component_id
        if self.affected_component_type:
            data['affected_component_type'] = self.affected_component_type
        if self.cause:
            data['cause'] = self.cause
        if self.resolution:
            data['resolution'] = self.resolution
        if self.resolved_at:
            data['resolved_at'] = self.resolved_at.isoformat()
        if self.estimated_restoration:
            data['estimated_restoration'] = self.estimated_restoration.isoformat()
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Incident':
        """Create instance from Neo4j result."""
        reported_at = data['reported_at']
        if isinstance(reported_at, str):
            reported_at = datetime.fromisoformat(reported_at.replace('Z', '+00:00'))
        
        resolved_at = data.get('resolved_at')
        if resolved_at and isinstance(resolved_at, str):
            resolved_at = datetime.fromisoformat(resolved_at.replace('Z', '+00:00'))
        
        estimated_restoration = data.get('estimated_restoration')
        if estimated_restoration and isinstance(estimated_restoration, str):
            estimated_restoration = datetime.fromisoformat(estimated_restoration.replace('Z', '+00:00'))
        
        return cls(
            id=data['id'],
            type=data['type'],
            severity=data['severity'],
            status=data['status'],
            description=data['description'],
            reported_at=reported_at,
            location=data.get('location'),
            affected_component_id=data.get('affected_component_id'),
            affected_component_type=data.get('affected_component_type'),
            cause=data.get('cause'),
            resolution=data.get('resolution'),
            resolved_at=resolved_at,
            estimated_restoration=estimated_restoration,
            affected_customers=data.get('affected_customers', 0),
            power_loss_mw=data.get('power_loss_mw', 0.0)
        )
    
    def __str__(self) -> str:
        """String representation."""
        return (f"Incident(id={self.id}, type={self.type}, "
                f"severity={self.severity}, status={self.status}, "
                f"customers={self.affected_customers})")
