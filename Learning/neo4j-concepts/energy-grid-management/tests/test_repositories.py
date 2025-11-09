"""
Tests for repository classes.
"""

import pytest
from src.connection import Neo4jConnection
from src.repositories.infrastructure_repo import InfrastructureRepository
from src.repositories.incident_repo import IncidentRepository
from src.repositories.sensor_repo import SensorRepository
from src.models.incident import Incident, IncidentType, IncidentSeverity, IncidentStatus
from src.models.sensor import Sensor, SensorType, SensorStatus
from datetime import datetime


@pytest.fixture
def connection():
    """Get database connection."""
    conn = Neo4jConnection()
    yield conn
    conn.close()


@pytest.fixture
def session(connection):
    """Get database session."""
    with connection.get_session() as sess:
        yield sess


def test_infrastructure_repo_get_power_plants(session):
    """Test fetching power plants."""
    repo = InfrastructureRepository(session)
    plants = repo.get_all_power_plants()
    assert isinstance(plants, list)
    if plants:
        assert plants[0].id is not None
        assert plants[0].name is not None


def test_infrastructure_repo_get_substations(session):
    """Test fetching substations."""
    repo = InfrastructureRepository(session)
    substations = repo.get_all_substations()
    assert isinstance(substations, list)
    if substations:
        assert substations[0].id is not None


def test_infrastructure_repo_statistics(session):
    """Test system statistics."""
    repo = InfrastructureRepository(session)
    stats = repo.get_system_statistics()
    assert 'total_plants' in stats
    assert 'total_substations' in stats
    assert 'total_customers' in stats


def test_incident_repo_create_and_get(session):
    """Test incident creation and retrieval."""
    repo = IncidentRepository(session)
    
    # Create test incident
    incident = Incident(
        incident_id="TEST-INC-001",
        type=IncidentType.EQUIPMENT_FAILURE,
        severity=IncidentSeverity.MEDIUM,
        status=IncidentStatus.REPORTED,
        description="Test incident",
        reported_at=datetime.now(),
        affected_customers=10,
        power_loss_mw=5.0
    )
    
    # Create
    incident_id = repo.create_incident(incident)
    assert incident_id == "TEST-INC-001"
    
    # Retrieve
    retrieved = repo.get_incident_by_id(incident_id)
    assert retrieved is not None
    assert retrieved.incident_id == incident_id
    assert retrieved.type == IncidentType.EQUIPMENT_FAILURE
    
    # Cleanup
    repo.delete_incident(incident_id)


def test_incident_repo_get_active(session):
    """Test getting active incidents."""
    repo = IncidentRepository(session)
    active = repo.get_active_incidents()
    assert isinstance(active, list)


def test_incident_repo_statistics(session):
    """Test incident statistics."""
    repo = IncidentRepository(session)
    stats = repo.get_incident_statistics()
    assert 'total_incidents' in stats


def test_sensor_repo_create_and_get(session):
    """Test sensor creation and retrieval."""
    repo = SensorRepository(session)
    
    # Create test sensor
    sensor = Sensor(
        sensor_id="TEST-SENS-001",
        name="Test Sensor",
        type=SensorType.VOLTAGE,
        status=SensorStatus.ACTIVE,
        location="Test Location",
        current_value=120.0,
        unit="kV",
        threshold_min=115.0,
        threshold_max=125.0,
        last_reading_at=datetime.now(),
        installed_at=datetime.now()
    )
    
    # Create
    sensor_id = repo.create_sensor(sensor)
    assert sensor_id == "TEST-SENS-001"
    
    # Retrieve
    retrieved = repo.get_sensor_by_id(sensor_id)
    assert retrieved is not None
    assert retrieved.sensor_id == sensor_id
    assert retrieved.type == SensorType.VOLTAGE
    
    # Cleanup
    repo.delete_sensor(sensor_id)


def test_sensor_repo_update_reading(session):
    """Test updating sensor reading."""
    repo = SensorRepository(session)
    
    # Create sensor
    sensor = Sensor(
        sensor_id="TEST-SENS-002",
        name="Test Sensor 2",
        type=SensorType.CURRENT,
        status=SensorStatus.ACTIVE,
        location="Test",
        current_value=100.0,
        unit="A",
        threshold_min=90.0,
        threshold_max=110.0,
        last_reading_at=datetime.now(),
        installed_at=datetime.now()
    )
    repo.create_sensor(sensor)
    
    # Update reading
    updated = repo.update_sensor_reading("TEST-SENS-002", 105.0)
    assert updated is True
    
    # Verify
    retrieved = repo.get_sensor_by_id("TEST-SENS-002")
    assert retrieved.current_value == 105.0
    
    # Cleanup
    repo.delete_sensor("TEST-SENS-002")


def test_sensor_repo_get_in_alarm(session):
    """Test getting sensors in alarm."""
    repo = SensorRepository(session)
    alarms = repo.get_sensors_in_alarm()
    assert isinstance(alarms, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
