"""
Substation Data Model

Represents electrical substations for voltage transformation and distribution.
"""

from dataclasses import dataclass
from datetime import date
from typing import Optional, Literal


SubstationType = Literal["transmission", "distribution", "switching"]
SubstationStatus = Literal["operational", "maintenance", "offline"]


@dataclass
class Substation:
    """
    Represents an electrical substation.
    
    Attributes:
        id: Unique identifier
        name: Substation name
        voltage_kv: Operating voltage in kilovolts
        capacity_mva: Transformer capacity in MVA
        type: Substation type (transmission, distribution, switching)
        status: Current operational status
        region: Geographic region
        location: Geographic coordinates (latitude, longitude)
        commissioned_date: Date substation was commissioned
        num_transformers: Number of transformers at this substation
    """
    
    id: str
    name: str
    voltage_kv: float
    capacity_mva: float
    type: SubstationType
    status: SubstationStatus
    region: str
    location: tuple[float, float]  # (latitude, longitude)
    commissioned_date: date
    num_transformers: int
    
    @property
    def is_transmission(self) -> bool:
        """Check if this is a transmission substation."""
        return self.type == "transmission"
    
    @property
    def is_distribution(self) -> bool:
        """Check if this is a distribution substation."""
        return self.type == "distribution"
    
    @property
    def is_high_voltage(self) -> bool:
        """Check if operating at high voltage (>= 230kV)."""
        return self.voltage_kv >= 230
    
    @property
    def is_operational(self) -> bool:
        """Check if substation is currently operational."""
        return self.status == "operational"
    
    def to_dict(self) -> dict:
        """Convert to dictionary for Neo4j."""
        return {
            "id": self.id,
            "name": self.name,
            "voltage_kv": self.voltage_kv,
            "capacity_mva": self.capacity_mva,
            "type": self.type,
            "status": self.status,
            "region": self.region,
            "location": f"point({{latitude: {self.location[0]}, longitude: {self.location[1]}}})",
            "commissioned_date": self.commissioned_date.isoformat(),
            "num_transformers": self.num_transformers
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Substation":
        """Create Substation instance from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            voltage_kv=float(data["voltage_kv"]),
            capacity_mva=float(data["capacity_mva"]),
            type=data["type"],
            status=data["status"],
            region=data["region"],
            location=(data["location"].latitude, data["location"].longitude) if hasattr(data["location"], "latitude") else (0.0, 0.0),
            commissioned_date=date.fromisoformat(data["commissioned_date"]),
            num_transformers=int(data["num_transformers"])
        )
    
    def __str__(self) -> str:
        """String representation."""
        return f"Substation({self.id}: {self.name}, {self.voltage_kv}kV, {self.region})"
