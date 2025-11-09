"""Pipeline segment model for water and gas networks."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any


class PipelineType(str, Enum):
    """Types of utility pipelines."""
    WATER = "water"
    GAS = "gas"
    COMBINED = "combined"


class PipelineMaterial(str, Enum):
    """Pipeline materials."""
    PVC = "PVC"
    STEEL = "steel"
    CAST_IRON = "cast_iron"
    COPPER = "copper"
    HDPE = "HDPE"
    DUCTILE_IRON = "ductile_iron"


class PipelineStatus(str, Enum):
    """Pipeline operational status."""
    ACTIVE = "active"
    MAINTENANCE = "maintenance"
    INACTIVE = "inactive"
    FAILED = "failed"


@dataclass
class PipelineSegment:
    """
    Represents a segment of utility pipeline (water or gas).
    
    Attributes:
        id: Unique identifier
        type: Water, gas, or combined
        material: Construction material
        diameter_mm: Inner diameter in millimeters
        length_m: Length in meters
        max_pressure_bar: Maximum operating pressure
        current_pressure_bar: Current pressure reading
        max_flow_rate: Maximum flow rate (liters/min for water, m³/h for gas)
        current_flow_rate: Current flow rate
        installation_date: Date of installation
        last_inspection_date: Last inspection date
        status: Operational status
        location: Geographic location description
        region: Service region
        latitude: GPS latitude
        longitude: GPS longitude
        age_years: Calculated age
    """
    
    id: str
    type: PipelineType
    material: PipelineMaterial
    diameter_mm: float
    length_m: float
    max_pressure_bar: float
    installation_date: datetime
    status: PipelineStatus = PipelineStatus.ACTIVE
    
    # Optional operational parameters
    current_pressure_bar: Optional[float] = None
    max_flow_rate: Optional[float] = None
    current_flow_rate: Optional[float] = None
    last_inspection_date: Optional[datetime] = None
    
    # Location information
    location: Optional[str] = None
    region: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    # Calculated fields
    age_years: Optional[int] = field(default=None, init=False)
    
    def __post_init__(self):
        """Calculate derived fields."""
        if self.installation_date:
            age_delta = datetime.now() - self.installation_date
            self.age_years = age_delta.days // 365
    
    def to_neo4j_properties(self) -> Dict[str, Any]:
        """Convert to Neo4j node properties."""
        props = {
            'id': self.id,
            'type': self.type.value,
            'material': self.material.value,
            'diameter_mm': self.diameter_mm,
            'length_m': self.length_m,
            'max_pressure_bar': self.max_pressure_bar,
            'installation_date': self.installation_date.isoformat(),
            'status': self.status.value,
        }
        
        # Add optional fields if present
        if self.current_pressure_bar is not None:
            props['current_pressure_bar'] = self.current_pressure_bar
        if self.max_flow_rate is not None:
            props['max_flow_rate'] = self.max_flow_rate
        if self.current_flow_rate is not None:
            props['current_flow_rate'] = self.current_flow_rate
        if self.last_inspection_date:
            props['last_inspection_date'] = self.last_inspection_date.isoformat()
        if self.location:
            props['location'] = self.location
        if self.region:
            props['region'] = self.region
        if self.latitude is not None:
            props['latitude'] = self.latitude
        if self.longitude is not None:
            props['longitude'] = self.longitude
        if self.age_years is not None:
            props['age_years'] = self.age_years
        
        return props
    
    def is_pressure_normal(self) -> bool:
        """Check if current pressure is within normal range."""
        if self.current_pressure_bar is None:
            return True
        return 0.8 * self.max_pressure_bar <= self.current_pressure_bar <= self.max_pressure_bar
    
    def is_flow_normal(self) -> bool:
        """Check if current flow is within normal range."""
        if self.current_flow_rate is None or self.max_flow_rate is None:
            return True
        return self.current_flow_rate <= self.max_flow_rate
    
    def needs_inspection(self, inspection_interval_days: int = 365) -> bool:
        """Determine if pipeline needs inspection."""
        if not self.last_inspection_date:
            return True
        
        days_since_inspection = (datetime.now() - self.last_inspection_date).days
        return days_since_inspection >= inspection_interval_days
    
    def calculate_risk_score(self) -> float:
        """
        Calculate risk score based on age, material, and status.
        Returns score from 0 (low risk) to 100 (high risk).
        """
        score = 0.0
        
        # Age factor (0-40 points)
        if self.age_years:
            if self.age_years > 50:
                score += 40
            elif self.age_years > 30:
                score += 30
            elif self.age_years > 20:
                score += 20
            else:
                score += self.age_years * 0.5
        
        # Material factor (0-30 points)
        material_risk = {
            PipelineMaterial.CAST_IRON: 30,
            PipelineMaterial.STEEL: 20,
            PipelineMaterial.DUCTILE_IRON: 15,
            PipelineMaterial.COPPER: 10,
            PipelineMaterial.HDPE: 5,
            PipelineMaterial.PVC: 5,
        }
        score += material_risk.get(self.material, 15)
        
        # Status factor (0-30 points)
        if self.status == PipelineStatus.FAILED:
            score += 30
        elif self.status == PipelineStatus.MAINTENANCE:
            score += 20
        elif not self.is_pressure_normal():
            score += 15
        elif not self.is_flow_normal():
            score += 10
        
        return min(score, 100.0)
