"""
Sensor Repository for Energy Grid Management
Handles database operations for IoT sensors and monitoring data.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from neo4j import Session

from ..models.sensor import Sensor, SensorType, SensorStatus


class SensorRepository:
    """Repository for sensor-related database operations."""
    
    def __init__(self, session: Session):
        """Initialize with Neo4j session."""
        self.session = session
    
    # CREATE operations
    
    def create_sensor(self, sensor: Sensor) -> str:
        """Create a new sensor in the database."""
        query = """
        CREATE (s:Sensor {
            sensor_id: $sensor_id,
            name: $name,
            type: $type,
            status: $status,
            location: $location,
            current_value: $current_value,
            unit: $unit,
            threshold_min: $threshold_min,
            threshold_max: $threshold_max,
            last_reading_at: datetime($last_reading_at),
            installed_at: datetime($installed_at),
            calibrated_at: $calibrated_at,
            firmware_version: $firmware_version
        })
        RETURN s.sensor_id as sensor_id
        """
        
        params = sensor.to_neo4j_dict()
        result = self.session.run(query, **params)
        record = result.single()
        return record["sensor_id"]
    
    def link_sensor_to_component(
        self, 
        sensor_id: str, 
        component_id: str, 
        component_type: str
    ) -> None:
        """Link sensor to monitored component."""
        query = f"""
        MATCH (s:Sensor {{sensor_id: $sensor_id}})
        MATCH (c:{component_type} {{id: $component_id}})
        CREATE (s)-[:MONITORS]->(c)
        """
        
        self.session.run(query, sensor_id=sensor_id, component_id=component_id)
    
    # READ operations
    
    def get_sensor_by_id(self, sensor_id: str) -> Optional[Sensor]:
        """Get sensor by ID."""
        query = """
        MATCH (s:Sensor {sensor_id: $sensor_id})
        RETURN s
        """
        
        result = self.session.run(query, sensor_id=sensor_id)
        record = result.single()
        
        if not record:
            return None
        
        return Sensor.from_neo4j_dict(dict(record["s"]))
    
    def get_all_sensors(self, limit: int = 100) -> List[Sensor]:
        """Get all sensors."""
        query = """
        MATCH (s:Sensor)
        RETURN s
        ORDER BY s.name
        LIMIT $limit
        """
        
        result = self.session.run(query, limit=limit)
        return [Sensor.from_neo4j_dict(dict(record["s"])) for record in result]
    
    def get_sensors_by_type(self, sensor_type: SensorType) -> List[Sensor]:
        """Get sensors by type."""
        query = """
        MATCH (s:Sensor {type: $type})
        RETURN s
        ORDER BY s.name
        """
        
        result = self.session.run(query, type=sensor_type.value)
        return [Sensor.from_neo4j_dict(dict(record["s"])) for record in result]
    
    def get_sensors_by_status(self, status: SensorStatus) -> List[Sensor]:
        """Get sensors by status."""
        query = """
        MATCH (s:Sensor {status: $status})
        RETURN s
        ORDER BY s.name
        """
        
        result = self.session.run(query, status=status.value)
        return [Sensor.from_neo4j_dict(dict(record["s"])) for record in result]
    
    def get_sensors_in_alarm(self) -> List[Sensor]:
        """Get all sensors currently in alarm state."""
        query = """
        MATCH (s:Sensor)
        WHERE s.status = 'active' 
          AND (s.current_value < s.threshold_min OR s.current_value > s.threshold_max)
        RETURN s
        ORDER BY 
            CASE 
                WHEN s.current_value > s.threshold_max 
                THEN s.current_value - s.threshold_max
                ELSE s.threshold_min - s.current_value
            END DESC
        """
        
        result = self.session.run(query)
        return [Sensor.from_neo4j_dict(dict(record["s"])) for record in result]
    
    def get_stale_sensors(self, minutes: int = 60) -> List[Sensor]:
        """Get sensors with stale readings."""
        query = """
        MATCH (s:Sensor)
        WHERE s.last_reading_at < datetime() - duration({minutes: $minutes})
        RETURN s
        ORDER BY s.last_reading_at ASC
        """
        
        result = self.session.run(query, minutes=minutes)
        return [Sensor.from_neo4j_dict(dict(record["s"])) for record in result]
    
    def get_sensors_for_component(
        self, 
        component_id: str, 
        component_type: str
    ) -> List[Sensor]:
        """Get all sensors monitoring a specific component."""
        query = f"""
        MATCH (s:Sensor)-[:MONITORS]->(c:{component_type} {{id: $component_id}})
        RETURN s
        ORDER BY s.type, s.name
        """
        
        result = self.session.run(query, component_id=component_id)
        return [Sensor.from_neo4j_dict(dict(record["s"])) for record in result]
    
    def get_sensors_by_location(self, location: str) -> List[Sensor]:
        """Get sensors at a specific location."""
        query = """
        MATCH (s:Sensor {location: $location})
        RETURN s
        ORDER BY s.type, s.name
        """
        
        result = self.session.run(query, location=location)
        return [Sensor.from_neo4j_dict(dict(record["s"])) for record in result]
    
    # UPDATE operations
    
    def update_sensor_reading(
        self, 
        sensor_id: str, 
        current_value: float,
        timestamp: Optional[datetime] = None
    ) -> bool:
        """Update sensor reading value and timestamp."""
        if timestamp is None:
            timestamp = datetime.now()
        
        query = """
        MATCH (s:Sensor {sensor_id: $sensor_id})
        SET s.current_value = $current_value,
            s.last_reading_at = datetime($timestamp)
        RETURN s
        """
        
        result = self.session.run(
            query,
            sensor_id=sensor_id,
            current_value=current_value,
            timestamp=timestamp.isoformat()
        )
        
        return result.single() is not None
    
    def update_sensor_status(self, sensor_id: str, status: SensorStatus) -> bool:
        """Update sensor status."""
        query = """
        MATCH (s:Sensor {sensor_id: $sensor_id})
        SET s.status = $status
        RETURN s
        """
        
        result = self.session.run(query, sensor_id=sensor_id, status=status.value)
        return result.single() is not None
    
    def update_sensor_thresholds(
        self, 
        sensor_id: str, 
        threshold_min: Optional[float] = None,
        threshold_max: Optional[float] = None
    ) -> bool:
        """Update sensor thresholds."""
        query = """
        MATCH (s:Sensor {sensor_id: $sensor_id})
        """
        
        set_clauses = []
        params = {"sensor_id": sensor_id}
        
        if threshold_min is not None:
            set_clauses.append("s.threshold_min = $threshold_min")
            params["threshold_min"] = threshold_min
        
        if threshold_max is not None:
            set_clauses.append("s.threshold_max = $threshold_max")
            params["threshold_max"] = threshold_max
        
        if not set_clauses:
            return False
        
        query += "SET " + ", ".join(set_clauses) + " RETURN s"
        
        result = self.session.run(query, **params)
        return result.single() is not None
    
    def update_sensor(self, sensor: Sensor) -> bool:
        """Update entire sensor record."""
        query = """
        MATCH (s:Sensor {sensor_id: $sensor_id})
        SET s.name = $name,
            s.type = $type,
            s.status = $status,
            s.location = $location,
            s.current_value = $current_value,
            s.unit = $unit,
            s.threshold_min = $threshold_min,
            s.threshold_max = $threshold_max,
            s.firmware_version = $firmware_version
        RETURN s
        """
        
        params = sensor.to_neo4j_dict()
        result = self.session.run(query, **params)
        return result.single() is not None
    
    def calibrate_sensor(self, sensor_id: str) -> bool:
        """Mark sensor as calibrated."""
        query = """
        MATCH (s:Sensor {sensor_id: $sensor_id})
        SET s.calibrated_at = datetime($timestamp)
        RETURN s
        """
        
        result = self.session.run(
            query, 
            sensor_id=sensor_id,
            timestamp=datetime.now().isoformat()
        )
        return result.single() is not None
    
    # DELETE operations
    
    def delete_sensor(self, sensor_id: str) -> bool:
        """Delete a sensor and its relationships."""
        query = """
        MATCH (s:Sensor {sensor_id: $sensor_id})
        DETACH DELETE s
        RETURN count(s) as deleted
        """
        
        result = self.session.run(query, sensor_id=sensor_id)
        record = result.single()
        return record["deleted"] > 0
    
    # ANALYTICS operations
    
    def get_sensor_statistics(self) -> Dict[str, Any]:
        """Get overall sensor statistics."""
        query = """
        MATCH (s:Sensor)
        WITH s
        RETURN 
            count(s) as total_sensors,
            count(CASE WHEN s.status = 'active' THEN 1 END) as active_sensors,
            count(CASE WHEN s.status = 'inactive' THEN 1 END) as inactive_sensors,
            count(CASE WHEN s.status = 'maintenance' THEN 1 END) as maintenance_sensors,
            count(CASE WHEN s.status = 'faulty' THEN 1 END) as faulty_sensors,
            count(CASE WHEN s.current_value < s.threshold_min 
                       OR s.current_value > s.threshold_max THEN 1 END) as in_alarm,
            count(CASE WHEN s.last_reading_at < datetime() - duration({minutes: 60}) 
                  THEN 1 END) as stale_sensors
        """
        
        result = self.session.run(query)
        record = result.single()
        return dict(record) if record else {}
    
    def get_sensor_stats_by_type(self) -> List[Dict[str, Any]]:
        """Get sensor statistics grouped by type."""
        query = """
        MATCH (s:Sensor)
        WITH s.type as sensor_type, s
        RETURN 
            sensor_type,
            count(s) as total,
            count(CASE WHEN s.status = 'active' THEN 1 END) as active,
            count(CASE WHEN s.current_value < s.threshold_min 
                       OR s.current_value > s.threshold_max THEN 1 END) as in_alarm,
            avg(s.current_value) as avg_value,
            min(s.current_value) as min_value,
            max(s.current_value) as max_value
        ORDER BY total DESC
        """
        
        result = self.session.run(query)
        return [dict(record) for record in result]
    
    def get_alarm_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get sensors that have been in alarm state recently."""
        query = """
        MATCH (s:Sensor)
        WHERE s.last_reading_at >= datetime() - duration({hours: $hours})
          AND (s.current_value < s.threshold_min OR s.current_value > s.threshold_max)
        RETURN 
            s.sensor_id as sensor_id,
            s.name as sensor_name,
            s.type as sensor_type,
            s.current_value as current_value,
            s.threshold_min as threshold_min,
            s.threshold_max as threshold_max,
            s.unit as unit,
            CASE 
                WHEN s.current_value < s.threshold_min THEN 'LOW'
                WHEN s.current_value > s.threshold_max THEN 'HIGH'
            END as alarm_type,
            s.last_reading_at as last_reading_at
        ORDER BY s.last_reading_at DESC
        """
        
        result = self.session.run(query, hours=hours)
        return [dict(record) for record in result]
    
    def get_sensors_needing_calibration(self, days: int = 90) -> List[Dict[str, Any]]:
        """Get sensors that need calibration."""
        query = """
        MATCH (s:Sensor)
        WHERE s.calibrated_at IS NULL 
           OR s.calibrated_at < datetime() - duration({days: $days})
        RETURN 
            s.sensor_id as sensor_id,
            s.name as sensor_name,
            s.type as sensor_type,
            s.location as location,
            s.calibrated_at as last_calibrated,
            duration.inDays(s.calibrated_at, datetime()).days as days_since_calibration
        ORDER BY days_since_calibration DESC
        """
        
        result = self.session.run(query, days=days)
        return [dict(record) for record in result]
    
    def get_component_sensor_health(
        self, 
        component_id: str, 
        component_type: str
    ) -> Dict[str, Any]:
        """Get sensor health for a specific component."""
        query = f"""
        MATCH (s:Sensor)-[:MONITORS]->(c:{component_type} {{id: $component_id}})
        RETURN 
            count(s) as total_sensors,
            count(CASE WHEN s.status = 'active' THEN 1 END) as active_sensors,
            count(CASE WHEN s.current_value < s.threshold_min 
                       OR s.current_value > s.threshold_max THEN 1 END) as in_alarm,
            count(CASE WHEN s.last_reading_at < datetime() - duration({{minutes: 60}}) 
                  THEN 1 END) as stale_sensors,
            collect({{
                sensor_id: s.sensor_id,
                name: s.name,
                type: s.type,
                status: s.status,
                current_value: s.current_value,
                unit: s.unit,
                in_alarm: s.current_value < s.threshold_min OR s.current_value > s.threshold_max
            }}) as sensors
        """
        
        result = self.session.run(query, component_id=component_id)
        record = result.single()
        return dict(record) if record else {}
