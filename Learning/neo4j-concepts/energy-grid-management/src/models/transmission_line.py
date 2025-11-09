"""
Transmission Line Model

Data model for electrical transmission lines.
"""

from dataclasses import dataclass
from datetime import date
from typing import Literal, Dict, Any, Optional


LineStatus = Literal['operational', 'maintenance', 'offline', 'decommissioned']
LineType = Literal['overhead', 'underground', 'submarine']


@dataclass
class TransmissionLine:
    """Model for transmission line relationships."""
    
    line_id: str
    from_substation_id: str
    to_substation_id: str
    capacity_mw: float
    voltage_kv: float
    distance_km: float
    loss_percent: float
    status: LineStatus
    line_type: LineType = 'overhead'
    install_date: Optional[date] = None
    last_maintenance: Optional[date] = None
    
    def __post_init__(self):
        """Validate data."""
        if self.capacity_mw <= 0:
            raise ValueError("Capacity must be positive")
        if self.voltage_kv <= 0:
            raise ValueError("Voltage must be positive")
        if self.distance_km <= 0:
            raise ValueError("Distance must be positive")
        if not 0 <= self.loss_percent <= 100:
            raise ValueError("Loss percent must be between 0 and 100")
    
    @property
    def is_operational(self) -> bool:
        """Check if line is operational."""
        return self.status == 'operational'
    
    @property
    def is_high_voltage(self, threshold: float = 345.0) -> bool:
        """Check if this is a high voltage line."""
        return self.voltage_kv >= threshold
    
    @property
    def is_long_distance(self, threshold: float = 100.0) -> bool:
        """Check if this is a long distance line."""
        return self.distance_km >= threshold
    
    @property
    def is_high_loss(self, threshold: float = 5.0) -> bool:
        """Check if line has high losses."""
        return self.loss_percent >= threshold
    
    @property
    def effective_capacity_mw(self) -> float:
        """Calculate effective capacity after losses."""
        return self.capacity_mw * (1 - self.loss_percent / 100)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Neo4j."""
        data = {
            'line_id': self.line_id,
            'capacity_mw': self.capacity_mw,
            'voltage_kv': self.voltage_kv,
            'distance_km': self.distance_km,
            'loss_percent': self.loss_percent,
            'status': self.status,
            'line_type': self.line_type,
        }
        
        if self.install_date:
            data['install_date'] = self.install_date.isoformat()
        if self.last_maintenance:
            data['last_maintenance'] = self.last_maintenance.isoformat()
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TransmissionLine':
        """Create instance from Neo4j result."""
        install_date = data.get('install_date')
        if install_date and isinstance(install_date, str):
            install_date = date.fromisoformat(install_date)
        
        last_maintenance = data.get('last_maintenance')
        if last_maintenance and isinstance(last_maintenance, str):
            last_maintenance = date.fromisoformat(last_maintenance)
        
        return cls(
            line_id=data['line_id'],
            from_substation_id=data.get('from_id', ''),
            to_substation_id=data.get('to_id', ''),
            capacity_mw=data['capacity_mw'],
            voltage_kv=data.get('voltage_kv', 0),
            distance_km=data['distance_km'],
            loss_percent=data['loss_percent'],
            status=data['status'],
            line_type=data.get('line_type', 'overhead'),
            install_date=install_date,
            last_maintenance=last_maintenance
        )
    
    def __str__(self) -> str:
        """String representation."""
        return (f"TransmissionLine(id={self.line_id}, "
                f"{self.from_substation_id}→{self.to_substation_id}, "
                f"{self.capacity_mw}MW, {self.distance_km}km, status={self.status})")
