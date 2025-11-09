"""
Tests for data models.
"""

import pytest
from datetime import datetime
from src.models.power_plant import PowerPlant, PlantType, PlantStatus
from src.models.substation import Substation, SubstationType, SubstationStatus
from src.models.transmission_line import TransmissionLine, LineType, LineStatus
from src.models.incident import Incident, IncidentType, IncidentSeverity, IncidentStatus
from src.models.sensor import Sensor, SensorType, SensorStatus


def test_power_plant_creation():
    """Test PowerPlant model creation."""
    plant = PowerPlant(
        id="PP001",
        name="Test Plant",
        type=PlantType.SOLAR,
        status=PlantStatus.OPERATIONAL,
        capacity_mw=100.0,
        location="Test Location"
    )
    
    assert plant.id == "PP001"
    assert plant.type == PlantType.SOLAR
    assert plant.is_renewable is True
    assert plant.is_operational is True


def test_power_plant_neo4j_conversion():
    """Test PowerPlant Neo4j conversion."""
    plant = PowerPlant(
        id="PP002",
        name="Test Plant 2",
        type=PlantType.WIND,
        status=PlantStatus.OPERATIONAL,
        capacity_mw=50.0,
        location="Location"
    )
    
    neo4j_dict = plant.to_neo4j_dict()
    assert neo4j_dict['id'] == "PP002"
    assert neo4j_dict['type'] == "wind"
    
    restored = PowerPlant.from_neo4j_dict(neo4j_dict)
    assert restored.id == plant.id
    assert restored.type == plant.type


def test_substation_creation():
    """Test Substation model creation."""
    substation = Substation(
        id="SS001",
        name="Test Substation",
        type=SubstationType.TRANSMISSION,
        status=SubstationStatus.OPERATIONAL,
        voltage_kv=230.0,
        capacity_mva=500.0,
        location="Test Location"
    )
    
    assert substation.id == "SS001"
    assert substation.is_transmission is True
    assert substation.is_high_voltage is True


def test_transmission_line_creation():
    """Test TransmissionLine model creation."""
    line = TransmissionLine(
        id="TL001",
        name="Test Line",
        type=LineType.OVERHEAD,
        status=LineStatus.ACTIVE,
        voltage_kv=345.0,
        capacity_mw=1000.0,
        distance_km=100.0,
        loss_percent=3.0
    )
    
    assert line.id == "TL001"
    assert line.is_high_voltage is True
    assert line.effective_capacity_mw == 970.0  # 1000 * (1 - 0.03)


def test_incident_creation():
    """Test Incident model creation."""
    incident = Incident(
        incident_id="INC001",
        type=IncidentType.EQUIPMENT_FAILURE,
        severity=IncidentSeverity.HIGH,
        status=IncidentStatus.REPORTED,
        description="Test incident",
        reported_at=datetime.now(),
        affected_customers=50,
        power_loss_mw=25.0
    )
    
    assert incident.incident_id == "INC001"
    assert incident.is_active is True
    assert incident.is_critical is False  # HIGH not CRITICAL


def test_incident_with_resolution():
    """Test Incident with resolution."""
    reported = datetime(2024, 1, 1, 10, 0)
    resolved = datetime(2024, 1, 1, 14, 0)
    
    incident = Incident(
        incident_id="INC002",
        type=IncidentType.OUTAGE,
        severity=IncidentSeverity.CRITICAL,
        status=IncidentStatus.RESOLVED,
        description="Test",
        reported_at=reported,
        resolved_at=resolved,
        affected_customers=100,
        power_loss_mw=50.0
    )
    
    assert incident.duration_minutes == 240  # 4 hours
    assert incident.is_critical is True


def test_sensor_creation():
    """Test Sensor model creation."""
    sensor = Sensor(
        sensor_id="SENS001",
        name="Test Sensor",
        type=SensorType.VOLTAGE,
        status=SensorStatus.ACTIVE,
        location="Test",
        current_value=120.0,
        unit="kV",
        threshold_min=115.0,
        threshold_max=125.0,
        last_reading_at=datetime.now(),
        installed_at=datetime.now()
    )
    
    assert sensor.sensor_id == "SENS001"
    assert sensor.is_in_alarm is False  # Within thresholds


def test_sensor_alarm_detection():
    """Test Sensor alarm detection."""
    sensor_high = Sensor(
        sensor_id="SENS002",
        name="High Sensor",
        type=SensorType.TEMPERATURE,
        status=SensorStatus.ACTIVE,
        location="Test",
        current_value=80.0,
        unit="°C",
        threshold_min=20.0,
        threshold_max=75.0,
        last_reading_at=datetime.now(),
        installed_at=datetime.now()
    )
    
    assert sensor_high.is_in_alarm is True
    assert sensor_high.alarm_type == "HIGH"
    
    sensor_low = Sensor(
        sensor_id="SENS003",
        name="Low Sensor",
        type=SensorType.VOLTAGE,
        status=SensorStatus.ACTIVE,
        location="Test",
        current_value=100.0,
        unit="kV",
        threshold_min=110.0,
        threshold_max=130.0,
        last_reading_at=datetime.now(),
        installed_at=datetime.now()
    )
    
    assert sensor_low.is_in_alarm is True
    assert sensor_low.alarm_type == "LOW"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
