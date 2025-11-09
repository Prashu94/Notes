"""
Storage Tank Model

Data model for water/gas storage facilities.
"""

from dataclasses import dataclass
from datetime import date
from typing import Literal, Dict, Any, Optional


TankType = Literal['elevated', 'ground', 'underground']
TankMaterial = Literal['steel', 'concrete', 'composite']
TankStatus = Literal['operational', 'maintenance', 'offline', 'decommissioned']


@dataclass
class StorageTank:
    """Model for storage tank nodes."""
    
    id: str
    name: str
    capacity_m3: float
    current_level_m3: float
    type: TankType
    material: TankMaterial
    status: TankStatus
    install_date: date
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    last_inspection: Optional[date] = None
    operator: Optional[str] = None
    
    def __post_init__(self):
        """Validate data after initialization."""
        if self.capacity_m3 <= 0:
            raise ValueError("Capacity must be positive")
        if self.current_level_m3 < 0:
            raise ValueError("Current level cannot be negative")
        if self.current_level_m3 > self.capacity_m3:
            raise ValueError("Current level cannot exceed capacity")
    
    @property
    def fill_percent(self) -> float:
        """Calculate fill percentage."""
        return (self.current_level_m3 / self.capacity_m3 * 100) if self.capacity_m3 > 0 else 0
    
    @property
    def is_operational(self) -> bool:
        """Check if tank is operational."""
        return self.status == 'operational'
    
    @property
    def is_low_level(self, threshold: float = 20.0) -> bool:
        """Check if tank level is below threshold."""
        return self.fill_percent < threshold
    
    @property
    def is_high_level(self, threshold: float = 90.0) -> bool:
        """Check if tank level is above threshold."""
        return self.fill_percent > threshold
    
    @property
    def available_capacity_m3(self) -> float:
        """Calculate available capacity."""
        return max(self.capacity_m3 - self.current_level_m3, 0)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Neo4j."""
        data = {
            'id': self.id,
            'name': self.name,
            'capacity_m3': self.capacity_m3,
            'current_level_m3': self.current_level_m3,
            'type': self.type,
            'material': self.material,
            'status': self.status,
            'install_date': self.install_date.isoformat(),
        }
        
        # Add location if available
        if self.latitude is not None and self.longitude is not None:
            data['location'] = f"point({{latitude: {self.latitude}, longitude: {self.longitude}}})"
        
        # Add optional fields
        if self.last_inspection:
            data['last_inspection'] = self.last_inspection.isoformat()
        if self.operator:
            data['operator'] = self.operator
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StorageTank':
        """Create instance from Neo4j result."""
        # Parse location if present
        latitude = None
        longitude = None
        if 'location' in data:
            location = data['location']
            if hasattr(location, 'latitude'):
                latitude = location.latitude
                longitude = location.longitude
        
        # Parse dates
        install_date = data['install_date']
        if isinstance(install_date, str):
            install_date = date.fromisoformat(install_date)
        
        last_inspection = data.get('last_inspection')
        if last_inspection and isinstance(last_inspection, str):
            last_inspection = date.fromisoformat(last_inspection)
        
        return cls(
            id=data['id'],
            name=data['name'],
            capacity_m3=data['capacity_m3'],
            current_level_m3=data['current_level_m3'],
            type=data['type'],
            material=data['material'],
            status=data['status'],
            install_date=install_date,
            latitude=latitude,
            longitude=longitude,
            last_inspection=last_inspection,
            operator=data.get('operator')
        )
    
    def __str__(self) -> str:
        """String representation."""
        return (f"StorageTank(id={self.id}, name={self.name}, "
                f"capacity={self.capacity_m3}m³, fill={self.fill_percent:.1f}%, "
                f"status={self.status})")


@dataclass
class PumpingStation:
    """Model for pumping station nodes."""
    
    id: str
    name: str
    capacity_m3_per_hour: float
    power_consumption_kw: float
    num_pumps: int
    operator: str
    efficiency_percent: float
    status: TankStatus  # Reuse same status types
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    install_date: Optional[date] = None
    last_maintenance: Optional[date] = None
    
    def __post_init__(self):
        """Validate data."""
        if self.capacity_m3_per_hour <= 0:
            raise ValueError("Capacity must be positive")
        if self.power_consumption_kw <= 0:
            raise ValueError("Power consumption must be positive")
        if self.num_pumps <= 0:
            raise ValueError("Number of pumps must be positive")
        if not 0 <= self.efficiency_percent <= 100:
            raise ValueError("Efficiency must be between 0 and 100")
    
    @property
    def is_operational(self) -> bool:
        """Check if station is operational."""
        return self.status == 'operational'
    
    @property
    def is_efficient(self, threshold: float = 80.0) -> bool:
        """Check if efficiency is above threshold."""
        return self.efficiency_percent >= threshold
    
    @property
    def capacity_per_pump_m3_per_hour(self) -> float:
        """Calculate capacity per pump."""
        return self.capacity_m3_per_hour / self.num_pumps if self.num_pumps > 0 else 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Neo4j."""
        data = {
            'id': self.id,
            'name': self.name,
            'capacity_m3_per_hour': self.capacity_m3_per_hour,
            'power_consumption_kw': self.power_consumption_kw,
            'num_pumps': self.num_pumps,
            'operator': self.operator,
            'efficiency_percent': self.efficiency_percent,
            'status': self.status,
        }
        
        if self.latitude is not None and self.longitude is not None:
            data['location'] = f"point({{latitude: {self.latitude}, longitude: {self.longitude}}})"
        
        if self.install_date:
            data['install_date'] = self.install_date.isoformat()
        if self.last_maintenance:
            data['last_maintenance'] = self.last_maintenance.isoformat()
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PumpingStation':
        """Create instance from Neo4j result."""
        latitude = None
        longitude = None
        if 'location' in data:
            location = data['location']
            if hasattr(location, 'latitude'):
                latitude = location.latitude
                longitude = location.longitude
        
        install_date = data.get('install_date')
        if install_date and isinstance(install_date, str):
            install_date = date.fromisoformat(install_date)
        
        last_maintenance = data.get('last_maintenance')
        if last_maintenance and isinstance(last_maintenance, str):
            last_maintenance = date.fromisoformat(last_maintenance)
        
        return cls(
            id=data['id'],
            name=data['name'],
            capacity_m3_per_hour=data['capacity_m3_per_hour'],
            power_consumption_kw=data['power_consumption_kw'],
            num_pumps=data['num_pumps'],
            operator=data['operator'],
            efficiency_percent=data['efficiency_percent'],
            status=data['status'],
            latitude=latitude,
            longitude=longitude,
            install_date=install_date,
            last_maintenance=last_maintenance
        )
    
    def __str__(self) -> str:
        """String representation."""
        return (f"PumpingStation(id={self.id}, name={self.name}, "
                f"capacity={self.capacity_m3_per_hour}m³/h, "
                f"efficiency={self.efficiency_percent}%, status={self.status})")
