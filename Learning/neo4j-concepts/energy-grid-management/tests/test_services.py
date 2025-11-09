"""
Tests for service layer classes.
"""

import pytest
from src.connection import Neo4jConnection
from src.services.grid_monitoring import GridMonitoringService
from src.services.outage_management import OutageManagementService
from src.services.maintenance_scheduler import MaintenanceSchedulerService
from src.services.load_forecasting import LoadForecastingService


@pytest.fixture
def driver():
    """Get database driver."""
    conn = Neo4jConnection()
    drv = conn.get_driver()
    yield drv
    conn.close()


def test_grid_monitoring_health_status(driver):
    """Test grid health status retrieval."""
    service = GridMonitoringService(driver)
    health = service.get_grid_health_status()
    
    assert 'total_plants' in health
    assert 'total_substations' in health
    assert 'overall_health_score' in health


def test_grid_monitoring_critical_components(driver):
    """Test critical components identification."""
    service = GridMonitoringService(driver)
    critical = service.get_critical_components()
    
    assert 'total_critical' in critical
    assert isinstance(critical['total_critical'], int)


def test_grid_monitoring_renewable_report(driver):
    """Test renewable energy report."""
    service = GridMonitoringService(driver)
    renewable = service.get_renewable_energy_report()
    
    assert 'total_renewable_capacity' in renewable
    assert 'renewable_percentage' in renewable
    assert 'by_type' in renewable


def test_grid_monitoring_regional_overview(driver):
    """Test regional overview."""
    service = GridMonitoringService(driver)
    regional = service.get_regional_overview()
    
    assert isinstance(regional, list)


def test_outage_management_get_active(driver):
    """Test getting active outages."""
    service = OutageManagementService(driver)
    outages = service.get_active_outages()
    
    assert isinstance(outages, list)


def test_outage_management_dashboard(driver):
    """Test outage dashboard."""
    service = OutageManagementService(driver)
    dashboard = service.get_outage_dashboard()
    
    assert 'statistics' in dashboard
    assert 'active_incidents' in dashboard


def test_maintenance_scheduler_priorities(driver):
    """Test maintenance priorities."""
    service = MaintenanceSchedulerService(driver)
    priorities = service.get_maintenance_priorities()
    
    assert isinstance(priorities, list)


def test_maintenance_scheduler_high_risk(driver):
    """Test high-risk component identification."""
    service = MaintenanceSchedulerService(driver)
    high_risk = service.identify_high_risk_components()
    
    assert isinstance(high_risk, list)


def test_load_forecasting_current_profile(driver):
    """Test current load profile."""
    service = LoadForecastingService(driver)
    profile = service.get_current_load_profile()
    
    assert 'timestamp' in profile
    assert 'capacity_analysis' in profile


def test_load_forecasting_growth_forecast(driver):
    """Test load growth forecast."""
    service = LoadForecastingService(driver)
    forecast = service.forecast_load_growth(years=5)
    
    assert 'parameters' in forecast
    assert 'total_forecast_mw' in forecast
    assert 'by_customer_type' in forecast


def test_load_forecasting_capacity_gaps(driver):
    """Test capacity gap identification."""
    service = LoadForecastingService(driver)
    gaps = service.identify_capacity_gaps(years=5)
    
    assert isinstance(gaps, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
