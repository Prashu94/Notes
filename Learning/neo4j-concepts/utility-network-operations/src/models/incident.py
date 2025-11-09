"""Incident model for leaks, bursts, and other network issues."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List


class IncidentType(str, Enum):
    """Types of utility incidents."""
    LEAK = "leak"
    BURST = "burst"
    CONTAMINATION = "contamination"
    PRESSURE_DROP = "pressure_drop"
    VALVE_FAILURE = "valve_failure"
    PUMP_FAILURE = "pump_failure"
    POWER_OUTAGE = "power_outage"
    FREEZING = "freezing"
    CORROSION = "corrosion"
    BLOCKAGE = "blockage"
    OTHER = "other"


class IncidentSeverity(str, Enum):
    """Incident severity levels."""
    CRITICAL = "critical"  # Major service disruption, safety risk
    HIGH = "high"          # Significant impact
    MEDIUM = "medium"      # Moderate impact
    LOW = "low"            # Minor issue


class IncidentStatus(str, Enum):
    """Incident resolution status."""
    REPORTED = "reported"
    INVESTIGATING = "investigating"
    CONFIRMED = "confirmed"
    REPAIRING = "repairing"
    RESOLVED = "resolved"
    CLOSED = "closed"


@dataclass
class IncidentImpact:
    """Impact metrics for an incident."""
    customers_affected: int = 0
    pipelines_affected: int = 0
    estimated_water_loss_liters: Optional[float] = None
    estimated_gas_loss_m3: Optional[float] = None
    estimated_cost: Optional[float] = None


@dataclass
class Incident:
    """
    Represents a utility network incident (leak, burst, contamination, etc.).
    
    Attributes:
        id: Unique incident identifier
        type: Incident type
        severity: Severity level
        status: Current status
        description: Detailed description
        location: Location description
        latitude: GPS latitude
        longitude: GPS longitude
        reported_date: When incident was reported
        confirmed_date: When incident was confirmed
        resolved_date: When incident was resolved
        reported_by: Who reported (customer ID, sensor ID, etc.)
        assigned_to: Team/technician assigned
        affected_infrastructure_ids: List of affected infrastructure IDs
        affected_customer_ids: List of affected customer IDs
        root_cause: Root cause analysis
        resolution_notes: How incident was resolved
        estimated_repair_time_hours: Estimated time to repair
        actual_repair_time_hours: Actual repair time
        impact: Impact metrics
    """
    
    id: str
    type: IncidentType
    severity: IncidentSeverity
    status: IncidentStatus
    description: str
    reported_date: datetime
    
    # Location
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    # Tracking dates
    confirmed_date: Optional[datetime] = None
    resolved_date: Optional[datetime] = None
    
    # Assignment and reporting
    reported_by: Optional[str] = None
    assigned_to: Optional[str] = None
    
    # Impact tracking
    affected_infrastructure_ids: List[str] = None
    affected_customer_ids: List[str] = None
    impact: Optional[IncidentImpact] = None
    
    # Resolution
    root_cause: Optional[str] = None
    resolution_notes: Optional[str] = None
    estimated_repair_time_hours: Optional[float] = None
    actual_repair_time_hours: Optional[float] = None
    
    def __post_init__(self):
        """Initialize default values."""
        if self.affected_infrastructure_ids is None:
            self.affected_infrastructure_ids = []
        if self.affected_customer_ids is None:
            self.affected_customer_ids = []
        if self.impact is None:
            self.impact = IncidentImpact()
    
    def to_neo4j_properties(self) -> Dict[str, Any]:
        """Convert to Neo4j node properties."""
        props = {
            'id': self.id,
            'type': self.type.value,
            'severity': self.severity.value,
            'status': self.status.value,
            'description': self.description,
            'reported_date': self.reported_date.isoformat(),
        }
        
        # Add optional fields
        if self.location:
            props['location'] = self.location
        if self.latitude is not None:
            props['latitude'] = self.latitude
        if self.longitude is not None:
            props['longitude'] = self.longitude
        if self.confirmed_date:
            props['confirmed_date'] = self.confirmed_date.isoformat()
        if self.resolved_date:
            props['resolved_date'] = self.resolved_date.isoformat()
        if self.reported_by:
            props['reported_by'] = self.reported_by
        if self.assigned_to:
            props['assigned_to'] = self.assigned_to
        if self.root_cause:
            props['root_cause'] = self.root_cause
        if self.resolution_notes:
            props['resolution_notes'] = self.resolution_notes
        if self.estimated_repair_time_hours is not None:
            props['estimated_repair_time_hours'] = self.estimated_repair_time_hours
        if self.actual_repair_time_hours is not None:
            props['actual_repair_time_hours'] = self.actual_repair_time_hours
        
        # Impact metrics
        if self.impact:
            props['customers_affected'] = self.impact.customers_affected
            props['pipelines_affected'] = self.impact.pipelines_affected
            if self.impact.estimated_water_loss_liters is not None:
                props['estimated_water_loss_liters'] = self.impact.estimated_water_loss_liters
            if self.impact.estimated_gas_loss_m3 is not None:
                props['estimated_gas_loss_m3'] = self.impact.estimated_gas_loss_m3
            if self.impact.estimated_cost is not None:
                props['estimated_cost'] = self.impact.estimated_cost
        
        return props
    
    def calculate_duration_hours(self) -> Optional[float]:
        """Calculate total duration from report to resolution."""
        if not self.resolved_date:
            return None
        
        delta = self.resolved_date - self.reported_date
        return delta.total_seconds() / 3600
    
    def calculate_response_time_hours(self) -> Optional[float]:
        """Calculate time from report to confirmation."""
        if not self.confirmed_date:
            return None
        
        delta = self.confirmed_date - self.reported_date
        return delta.total_seconds() / 3600
    
    def is_active(self) -> bool:
        """Check if incident is still active (not resolved or closed)."""
        return self.status not in [IncidentStatus.RESOLVED, IncidentStatus.CLOSED]
    
    def calculate_priority_score(self) -> float:
        """
        Calculate priority score (0-100) for incident triage.
        Higher score = higher priority.
        """
        score = 0.0
        
        # Severity base score (0-40 points)
        severity_scores = {
            IncidentSeverity.CRITICAL: 40,
            IncidentSeverity.HIGH: 30,
            IncidentSeverity.MEDIUM: 20,
            IncidentSeverity.LOW: 10,
        }
        score += severity_scores.get(self.severity, 20)
        
        # Type factor (0-30 points)
        type_scores = {
            IncidentType.BURST: 30,
            IncidentType.CONTAMINATION: 28,
            IncidentType.PUMP_FAILURE: 25,
            IncidentType.LEAK: 20,
            IncidentType.PRESSURE_DROP: 15,
            IncidentType.VALVE_FAILURE: 15,
            IncidentType.BLOCKAGE: 10,
            IncidentType.CORROSION: 10,
        }
        score += type_scores.get(self.type, 10)
        
        # Impact factor (0-30 points)
        if self.impact:
            if self.impact.customers_affected > 1000:
                score += 30
            elif self.impact.customers_affected > 500:
                score += 25
            elif self.impact.customers_affected > 100:
                score += 20
            elif self.impact.customers_affected > 10:
                score += 15
            elif self.impact.customers_affected > 0:
                score += 10
        
        return min(score, 100.0)
    
    def estimate_total_cost(self) -> float:
        """Estimate total incident cost if not already calculated."""
        if self.impact and self.impact.estimated_cost is not None:
            return self.impact.estimated_cost
        
        # Base cost by incident type
        base_costs = {
            IncidentType.BURST: 50000,
            IncidentType.CONTAMINATION: 100000,
            IncidentType.PUMP_FAILURE: 30000,
            IncidentType.LEAK: 10000,
            IncidentType.VALVE_FAILURE: 5000,
            IncidentType.PRESSURE_DROP: 3000,
            IncidentType.BLOCKAGE: 2000,
        }
        cost = base_costs.get(self.type, 5000)
        
        # Multiply by severity
        severity_multipliers = {
            IncidentSeverity.CRITICAL: 3.0,
            IncidentSeverity.HIGH: 2.0,
            IncidentSeverity.MEDIUM: 1.5,
            IncidentSeverity.LOW: 1.0,
        }
        cost *= severity_multipliers.get(self.severity, 1.5)
        
        # Add customer impact cost
        if self.impact and self.impact.customers_affected > 0:
            cost += self.impact.customers_affected * 50
        
        # Add water/gas loss cost
        if self.impact:
            if self.impact.estimated_water_loss_liters:
                cost += self.impact.estimated_water_loss_liters * 0.002  # $0.002 per liter
            if self.impact.estimated_gas_loss_m3:
                cost += self.impact.estimated_gas_loss_m3 * 0.50  # $0.50 per m³
        
        return round(cost, 2)
