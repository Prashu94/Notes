"""Smart meter model for consumption tracking."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List


class MeterType(str, Enum):
    """Types of utility meters."""
    WATER = "water"
    GAS = "gas"
    COMBINED = "combined"


class MeterStatus(str, Enum):
    """Meter operational status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    FAULTY = "faulty"
    MAINTENANCE = "maintenance"
    REPLACED = "replaced"


@dataclass
class MeterReading:
    """Single meter reading entry."""
    timestamp: datetime
    value: float
    unit: str  # m³, liters, kWh, etc.


@dataclass
class Meter:
    """
    Represents a smart utility meter.
    
    Attributes:
        id: Unique meter identifier
        type: Water, gas, or combined
        model: Manufacturer model number
        serial_number: Device serial number
        installation_date: Installation date
        last_reading_date: Most recent reading timestamp
        last_reading_value: Most recent reading value
        total_consumption: Cumulative consumption
        unit: Measurement unit
        status: Operational status
        location: Installation location
        latitude: GPS latitude
        longitude: GPS longitude
        battery_level: Battery percentage (0-100)
        signal_strength: Communication signal strength (0-100)
        firmware_version: Device firmware version
        reading_interval_minutes: How often meter reports
    """
    
    id: str
    type: MeterType
    model: str
    serial_number: str
    installation_date: datetime
    unit: str = "m³"
    status: MeterStatus = MeterStatus.ACTIVE
    
    # Reading information
    last_reading_date: Optional[datetime] = None
    last_reading_value: Optional[float] = None
    total_consumption: float = 0.0
    
    # Location
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    # IoT/Smart meter features
    battery_level: Optional[int] = None
    signal_strength: Optional[int] = None
    firmware_version: Optional[str] = None
    reading_interval_minutes: int = 60
    
    # Historical readings (not stored in Neo4j properties)
    readings_history: List[MeterReading] = field(default_factory=list, repr=False)
    
    def to_neo4j_properties(self) -> Dict[str, Any]:
        """Convert to Neo4j node properties."""
        props = {
            'id': self.id,
            'type': self.type.value,
            'model': self.model,
            'serial_number': self.serial_number,
            'installation_date': self.installation_date.isoformat(),
            'unit': self.unit,
            'status': self.status.value,
            'total_consumption': self.total_consumption,
            'reading_interval_minutes': self.reading_interval_minutes,
        }
        
        # Add optional fields
        if self.last_reading_date:
            props['last_reading_date'] = self.last_reading_date.isoformat()
        if self.last_reading_value is not None:
            props['last_reading_value'] = self.last_reading_value
        if self.location:
            props['location'] = self.location
        if self.latitude is not None:
            props['latitude'] = self.latitude
        if self.longitude is not None:
            props['longitude'] = self.longitude
        if self.battery_level is not None:
            props['battery_level'] = self.battery_level
        if self.signal_strength is not None:
            props['signal_strength'] = self.signal_strength
        if self.firmware_version:
            props['firmware_version'] = self.firmware_version
        
        return props
    
    def add_reading(self, value: float, timestamp: Optional[datetime] = None):
        """Add a new meter reading."""
        if timestamp is None:
            timestamp = datetime.now()
        
        reading = MeterReading(timestamp=timestamp, value=value, unit=self.unit)
        self.readings_history.append(reading)
        
        # Update current reading
        self.last_reading_date = timestamp
        self.last_reading_value = value
        
        # Update total consumption
        if len(self.readings_history) > 1:
            previous_value = self.readings_history[-2].value
            consumption = value - previous_value
            if consumption > 0:
                self.total_consumption += consumption
    
    def is_battery_low(self, threshold: int = 20) -> bool:
        """Check if battery needs replacement."""
        if self.battery_level is None:
            return False
        return self.battery_level < threshold
    
    def is_signal_weak(self, threshold: int = 30) -> bool:
        """Check if signal strength is weak."""
        if self.signal_strength is None:
            return False
        return self.signal_strength < threshold
    
    def is_stale(self, max_age_hours: int = 24) -> bool:
        """Check if meter reading is stale (no recent updates)."""
        if not self.last_reading_date:
            return True
        
        hours_since_reading = (datetime.now() - self.last_reading_date).total_seconds() / 3600
        expected_readings = max_age_hours * 60 / self.reading_interval_minutes
        
        return hours_since_reading > expected_readings * self.reading_interval_minutes / 60
    
    def calculate_average_consumption(self, days: int = 30) -> Optional[float]:
        """Calculate average daily consumption."""
        if not self.readings_history or len(self.readings_history) < 2:
            return None
        
        cutoff_date = datetime.now()
        cutoff_date = cutoff_date.replace(day=cutoff_date.day - days)
        
        recent_readings = [r for r in self.readings_history if r.timestamp >= cutoff_date]
        if len(recent_readings) < 2:
            return None
        
        total = recent_readings[-1].value - recent_readings[0].value
        time_span = (recent_readings[-1].timestamp - recent_readings[0].timestamp).days
        
        if time_span == 0:
            return None
        
        return total / time_span
    
    def detect_anomaly(self, threshold_multiplier: float = 2.0) -> bool:
        """
        Detect consumption anomaly based on historical average.
        Returns True if current consumption is abnormally high.
        """
        if len(self.readings_history) < 10:
            return False
        
        avg = self.calculate_average_consumption(days=30)
        if avg is None:
            return False
        
        # Calculate consumption for last reading
        if len(self.readings_history) >= 2:
            recent = self.readings_history[-1]
            previous = self.readings_history[-2]
            time_diff_hours = (recent.timestamp - previous.timestamp).total_seconds() / 3600
            
            if time_diff_hours > 0:
                hourly_consumption = (recent.value - previous.value) / time_diff_hours
                daily_rate = hourly_consumption * 24
                
                return daily_rate > avg * threshold_multiplier
        
        return False
