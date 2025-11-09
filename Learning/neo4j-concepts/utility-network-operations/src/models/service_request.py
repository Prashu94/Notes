"""Service request model for customer support tickets."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any


class RequestType(str, Enum):
    """Types of service requests."""
    LEAK_REPORT = "leak_report"
    NO_WATER = "no_water"
    NO_GAS = "no_gas"
    LOW_PRESSURE = "low_pressure"
    WATER_QUALITY = "water_quality"
    BILLING_INQUIRY = "billing_inquiry"
    METER_ISSUE = "meter_issue"
    NEW_CONNECTION = "new_connection"
    DISCONNECTION = "disconnection"
    MAINTENANCE = "maintenance"
    EMERGENCY = "emergency"
    OTHER = "other"


class RequestStatus(str, Enum):
    """Service request status."""
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    ON_HOLD = "on_hold"
    RESOLVED = "resolved"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class RequestPriority(str, Enum):
    """Service request priority levels."""
    CRITICAL = "critical"  # Emergency, safety issue
    HIGH = "high"          # Major service disruption
    MEDIUM = "medium"      # Minor issue, can wait
    LOW = "low"            # Non-urgent inquiry


@dataclass
class ServiceRequest:
    """
    Represents a customer service request or work order.
    
    Attributes:
        id: Unique request identifier
        type: Request type
        priority: Priority level
        status: Current status
        customer_id: Customer who submitted request
        description: Detailed description
        location: Location of issue
        latitude: GPS latitude
        longitude: GPS longitude
        created_date: When request was created
        assigned_date: When assigned to technician
        scheduled_date: Scheduled service date
        completed_date: When work was completed
        assigned_to: Technician/team ID
        estimated_duration_hours: Estimated time to complete
        actual_duration_hours: Actual time taken
        resolution_notes: Notes on how issue was resolved
        customer_satisfaction: Customer rating (1-5)
        follow_up_required: Whether follow-up is needed
        related_incident_id: Related incident if any
    """
    
    id: str
    type: RequestType
    priority: RequestPriority
    status: RequestStatus
    customer_id: str
    description: str
    created_date: datetime
    
    # Location information
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    # Assignment and scheduling
    assigned_date: Optional[datetime] = None
    scheduled_date: Optional[datetime] = None
    completed_date: Optional[datetime] = None
    assigned_to: Optional[str] = None
    
    # Time tracking
    estimated_duration_hours: Optional[float] = None
    actual_duration_hours: Optional[float] = None
    
    # Resolution
    resolution_notes: Optional[str] = None
    customer_satisfaction: Optional[int] = None
    follow_up_required: bool = False
    related_incident_id: Optional[str] = None
    
    def to_neo4j_properties(self) -> Dict[str, Any]:
        """Convert to Neo4j node properties."""
        props = {
            'id': self.id,
            'type': self.type.value,
            'priority': self.priority.value,
            'status': self.status.value,
            'customer_id': self.customer_id,
            'description': self.description,
            'created_date': self.created_date.isoformat(),
            'follow_up_required': self.follow_up_required,
        }
        
        # Add optional fields
        if self.location:
            props['location'] = self.location
        if self.latitude is not None:
            props['latitude'] = self.latitude
        if self.longitude is not None:
            props['longitude'] = self.longitude
        if self.assigned_date:
            props['assigned_date'] = self.assigned_date.isoformat()
        if self.scheduled_date:
            props['scheduled_date'] = self.scheduled_date.isoformat()
        if self.completed_date:
            props['completed_date'] = self.completed_date.isoformat()
        if self.assigned_to:
            props['assigned_to'] = self.assigned_to
        if self.estimated_duration_hours is not None:
            props['estimated_duration_hours'] = self.estimated_duration_hours
        if self.actual_duration_hours is not None:
            props['actual_duration_hours'] = self.actual_duration_hours
        if self.resolution_notes:
            props['resolution_notes'] = self.resolution_notes
        if self.customer_satisfaction is not None:
            props['customer_satisfaction'] = self.customer_satisfaction
        if self.related_incident_id:
            props['related_incident_id'] = self.related_incident_id
        
        return props
    
    def is_overdue(self) -> bool:
        """Check if request is overdue based on priority and age."""
        if self.status in [RequestStatus.RESOLVED, RequestStatus.CLOSED, RequestStatus.CANCELLED]:
            return False
        
        age_hours = (datetime.now() - self.created_date).total_seconds() / 3600
        
        # SLA thresholds by priority
        sla_hours = {
            RequestPriority.CRITICAL: 2,
            RequestPriority.HIGH: 24,
            RequestPriority.MEDIUM: 72,
            RequestPriority.LOW: 168,  # 1 week
        }
        
        threshold = sla_hours.get(self.priority, 72)
        return age_hours > threshold
    
    def calculate_response_time_hours(self) -> Optional[float]:
        """Calculate time from creation to assignment."""
        if not self.assigned_date:
            return None
        
        delta = self.assigned_date - self.created_date
        return delta.total_seconds() / 3600
    
    def calculate_resolution_time_hours(self) -> Optional[float]:
        """Calculate total time from creation to completion."""
        if not self.completed_date:
            return None
        
        delta = self.completed_date - self.created_date
        return delta.total_seconds() / 3600
    
    def meets_sla(self) -> Optional[bool]:
        """Check if request met SLA targets."""
        if self.status not in [RequestStatus.RESOLVED, RequestStatus.CLOSED]:
            return None
        
        resolution_time = self.calculate_resolution_time_hours()
        if resolution_time is None:
            return None
        
        # SLA targets by priority
        sla_targets = {
            RequestPriority.CRITICAL: 4,
            RequestPriority.HIGH: 48,
            RequestPriority.MEDIUM: 120,
            RequestPriority.LOW: 240,
        }
        
        target = sla_targets.get(self.priority, 120)
        return resolution_time <= target
    
    def calculate_urgency_score(self) -> float:
        """
        Calculate urgency score (0-100) based on priority, age, and status.
        Higher score = more urgent.
        """
        score = 0.0
        
        # Priority base score (0-50 points)
        priority_scores = {
            RequestPriority.CRITICAL: 50,
            RequestPriority.HIGH: 35,
            RequestPriority.MEDIUM: 20,
            RequestPriority.LOW: 10,
        }
        score += priority_scores.get(self.priority, 20)
        
        # Age factor (0-30 points)
        age_hours = (datetime.now() - self.created_date).total_seconds() / 3600
        if age_hours > 72:
            score += 30
        elif age_hours > 48:
            score += 25
        elif age_hours > 24:
            score += 20
        elif age_hours > 12:
            score += 15
        elif age_hours > 6:
            score += 10
        else:
            score += age_hours
        
        # Status factor (0-20 points)
        if self.status == RequestStatus.PENDING:
            score += 20
        elif self.status == RequestStatus.ASSIGNED:
            score += 15
        elif self.status == RequestStatus.ON_HOLD:
            score += 10
        elif self.status == RequestStatus.IN_PROGRESS:
            score += 5
        
        return min(score, 100.0)
