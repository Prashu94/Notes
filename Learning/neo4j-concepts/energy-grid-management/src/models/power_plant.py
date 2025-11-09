"""
Power Plant Data Model

Represents electrical power generation facilities.
"""

from dataclasses import dataclass
from datetime import date
from typing import Optional, Literal


PlantType = Literal["coal", "nuclear", "solar", "wind", "hydro", "natural_gas"]
PlantStatus = Literal["operational", "maintenance", "offline", "decommissioned"]


@dataclass
class PowerPlant:
    """
    Represents a power generation facility.
    
    Attributes:
        id: Unique identifier
        name: Plant name
        type: Generation type (coal, nuclear, solar, wind, hydro, natural_gas)
        capacity_mw: Generation capacity in megawatts
        efficiency_percent: Operational efficiency percentage
        status: Current operational status
        commissioned_date: Date plant was commissioned
        operator: Operating company name
        location: Geographic coordinates (latitude, longitude)
        emissions_tons_per_year: Annual CO2 emissions in tons
        description: Additional details about the plant
    """
    
    id: str
    name: str
    type: PlantType
    capacity_mw: float
    efficiency_percent: float
    status: PlantStatus
    commissioned_date: date
    operator: str
    location: tuple[float, float]  # (latitude, longitude)
    emissions_tons_per_year: float
    description: Optional[str] = None
    
    @property
    def is_renewable(self) -> bool:
        """Check if plant uses renewable energy source."""
        return self.type in ["solar", "wind", "hydro"]
    
    @property
    def is_operational(self) -> bool:
        """Check if plant is currently operational."""
        return self.status == "operational"
    
    @property
    def is_clean_energy(self) -> bool:
        """Check if plant is low/zero emission."""
        return self.type in ["solar", "wind", "hydro", "nuclear"]
    
    def to_dict(self) -> dict:
        """Convert to dictionary for Neo4j."""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "capacity_mw": self.capacity_mw,
            "efficiency_percent": self.efficiency_percent,
            "status": self.status,
            "commissioned_date": self.commissioned_date.isoformat(),
            "operator": self.operator,
            "location": f"point({{latitude: {self.location[0]}, longitude: {self.location[1]}}})",
            "emissions_tons_per_year": self.emissions_tons_per_year,
            "description": self.description or ""
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "PowerPlant":
        """Create PowerPlant instance from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            type=data["type"],
            capacity_mw=float(data["capacity_mw"]),
            efficiency_percent=float(data["efficiency_percent"]),
            status=data["status"],
            commissioned_date=date.fromisoformat(data["commissioned_date"]),
            operator=data["operator"],
            location=(data["location"].latitude, data["location"].longitude) if hasattr(data["location"], "latitude") else (0.0, 0.0),
            emissions_tons_per_year=float(data["emissions_tons_per_year"]),
            description=data.get("description")
        )
    
    def __str__(self) -> str:
        """String representation."""
        return f"PowerPlant({self.id}: {self.name}, {self.type}, {self.capacity_mw}MW)"
