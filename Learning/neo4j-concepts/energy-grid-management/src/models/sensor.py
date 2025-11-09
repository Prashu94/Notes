"""
Sensor Model

Data model for IoT sensors monitoring grid equipment.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Literal, Dict, Any, Optional


SensorType = Literal['voltage', 'current', 'temperature', 'vibration', 'power', 'frequency']
SensorStatus = Literal['operational', 'maintenance', 'offline', 'error']


@dataclass
class Sensor:
    """Model for IoT sensor nodes."""
    
    id: str
    type: SensorType
    status: SensorStatus
    monitored_component_id: str
    monitored_component_type: str
    current_value: float
    unit: str
    threshold_min: Optional[float] = None
    threshold_max: Optional[float] = None
    last_reading_time: Optional[datetime] = None
    install_date: Optional[datetime] = None
    location: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    
    @property
    def is_operational(self) -> bool:
        """Check if sensor is operational."""
        return self.status == 'operational'
    
    @property
    def is_in_alarm(self) -> bool:
        """Check if current value exceeds thresholds."""
        if self.threshold_min is not None and self.current_value < self.threshold_min:
            return True
        if self.threshold_max is not None and self.current_value > self.threshold_max:
            return True
        return False
    
    @property
    def alarm_type(self) -> Optional[str]:
        """Determine alarm type if any."""
        if not self.is_in_alarm:
            return None
        if self.threshold_min is not None and self.current_value < self.threshold_min:
            return 'LOW'
        if self.threshold_max is not None and self.current_value > self.threshold_max:
            return 'HIGH'
        return None
    
    @property
    def is_reading_stale(self, max_age_minutes: int = 15) -> bool:
        """Check if last reading is too old."""
        if not self.last_reading_time:
            return True
        age = datetime.now() - self.last_reading_time
        return age.total_seconds() / 60 > max_age_minutes
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Neo4j."""
        data = {
            'id': self.id,
            'type': self.type,
            'status': self.status,
            'monitored_component_id': self.monitored_component_id,
            'monitored_component_type': self.monitored_component_type,
            'current_value': self.current_value,
            'unit': self.unit,
        }
        
        if self.threshold_min is not None:
            data['threshold_min'] = self.threshold_min
        if self.threshold_max is not None:
            data['threshold_max'] = self.threshold_max
        if self.last_reading_time:
            data['last_reading_time'] = self.last_reading_time.isoformat()
        if self.install_date:
            data['install_date'] = self.install_date.isoformat()
        if self.location:
            data['location'] = self.location
        if self.manufacturer:
            data['manufacturer'] = self.manufacturer
        if self.model:
            data['model'] = self.model
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Sensor':
        """Create instance from Neo4j result."""
        last_reading_time = data.get('last_reading_time')
        if last_reading_time and isinstance(last_reading_time, str):
            last_reading_time = datetime.fromisoformat(last_reading_time.replace('Z', '+00:00'))
        
        install_date = data.get('install_date')
        if install_date and isinstance(install_date, str):
            install_date = datetime.fromisoformat(install_date.replace('Z', '+00:00'))
        
        return cls(
            id=data['id'],
            type=data['type'],
            status=data['status'],
            monitored_component_id=data['monitored_component_id'],
            monitored_component_type=data['monitored_component_type'],
            current_value=data['current_value'],
            unit=data['unit'],
            threshold_min=data.get('threshold_min'),
            threshold_max=data.get('threshold_max'),
            last_reading_time=last_reading_time,
            install_date=install_date,
            location=data.get('location'),
            manufacturer=data.get('manufacturer'),
            model=data.get('model')
        )
    
    def __str__(self) -> str:
        """String representation."""
        alarm = f" [ALARM: {self.alarm_type}]" if self.is_in_alarm else ""
        return (f"Sensor(id={self.id}, type={self.type}, "
                f"value={self.current_value}{self.unit}, "
                f"status={self.status}{alarm})")
