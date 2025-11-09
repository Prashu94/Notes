"""Network monitoring example demonstrating real-time monitoring features."""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from src.connection import Neo4jConnection
from src.repositories.infrastructure_repo import InfrastructureRepository
from src.repositories.incident_repo import IncidentRepository
from src.services.network_monitoring import NetworkMonitoringService


def main():
    """Demonstrate network monitoring capabilities."""
    
    print("=" * 60)
    print("Utility Network Operations - Network Monitoring Example")
    print("=" * 60)
    
    conn = Neo4jConnection()
    infra_repo = InfrastructureRepository(conn)
    incident_repo = IncidentRepository(conn)
    monitoring_service = NetworkMonitoringService(infra_repo, incident_repo)
    
    # 1. Get Overall Network Status
    print("\n1. Overall Network Status")
    print("-" * 60)
    status = monitoring_service.get_network_status()
    
    print(f"Health Score: {status['health_score']}/100")
    print(f"Status: {status['status']}")
    print(f"Active Incidents: {status['active_incidents']}")
    print(f"Total Infrastructure: {status['total_infrastructure']}")
    
    print("\nInfrastructure Breakdown:")
    infra = status['infrastructure']
    print(f"  - Pipelines: {infra['total_pipelines']} ({infra['active_pipelines']} active)")
    print(f"  - Meters: {infra['total_meters']} ({infra['active_meters']} active)")
    print(f"  - Storage Tanks: {infra['total_tanks']}")
    
    if status['anomalies']:
        print(f"\n⚠ Anomalies Detected: {len(status['anomalies'])}")
        for anomaly in status['anomalies'][:5]:
            print(f"  - {anomaly['type']}: {anomaly['description']}")
    
    if status['alerts']:
        print(f"\n⚠ Active Alerts: {len(status['alerts'])}")
        for alert in status['alerts'][:5]:
            print(f"  - [{alert['severity']}] {alert['message']}")
    
    # 2. Pressure Monitoring Dashboard
    print("\n2. Pressure Monitoring Dashboard")
    print("-" * 60)
    pressure_dashboard = monitoring_service.get_pressure_monitoring_dashboard()
    
    stats = pressure_dashboard['statistics']
    print(f"Average Pressure: {stats['average_pressure']:.2f} PSI")
    print(f"Min Pressure: {stats['min_pressure']:.2f} PSI")
    print(f"Max Pressure: {stats['max_pressure']:.2f} PSI")
    
    if pressure_dashboard['anomalies']:
        print(f"\n⚠ Pressure Anomalies: {len(pressure_dashboard['anomalies'])}")
        for anomaly in pressure_dashboard['anomalies'][:5]:
            print(f"  - {anomaly['pipeline_id']}: {anomaly['current_pressure']:.2f} PSI "
                  f"(expected: {anomaly['expected_range']})")
    
    # 3. Meter Health Dashboard
    print("\n3. Meter Health Dashboard")
    print("-" * 60)
    meter_dashboard = monitoring_service.get_meter_health_dashboard()
    
    print(f"Total Meters: {meter_dashboard['total_meters']}")
    print(f"Healthy: {meter_dashboard['healthy_meters']}")
    print(f"Issues: {meter_dashboard['meters_with_issues']}")
    
    issues = meter_dashboard['issues']
    if issues['low_battery']:
        print(f"\n⚠ Low Battery: {len(issues['low_battery'])} meters")
        for meter in issues['low_battery'][:3]:
            print(f"  - {meter['meter_id']}: {meter['battery_level']}%")
    
    if issues['weak_signal']:
        print(f"\n⚠ Weak Signal: {len(issues['weak_signal'])} meters")
        for meter in issues['weak_signal'][:3]:
            print(f"  - {meter['meter_id']}: {meter['signal_strength']}%")
    
    if issues['stale_readings']:
        print(f"\n⚠ Stale Readings: {len(issues['stale_readings'])} meters")
        for meter in issues['stale_readings'][:3]:
            print(f"  - {meter['meter_id']}: Last reading {meter['hours_since_reading']:.1f} hours ago")
    
    # 4. Regional Status
    print("\n4. Regional Status Overview")
    print("-" * 60)
    regional_status = monitoring_service.get_regional_status()
    
    for region in regional_status:
        print(f"\nRegion: {region['region']}")
        print(f"  Health Score: {region['health_score']}/100")
        print(f"  Pipelines: {region['pipeline_count']}")
        print(f"  Customers: {region['customer_count']}")
        print(f"  Active Incidents: {region['active_incidents']}")
        print(f"  Avg Pressure: {region['avg_pressure']:.2f} PSI")
    
    # 5. High Risk Infrastructure
    print("\n5. High Risk Infrastructure")
    print("-" * 60)
    high_risk = monitoring_service.get_high_risk_infrastructure()
    
    if high_risk['pipelines']:
        print(f"\n⚠ High Risk Pipelines: {len(high_risk['pipelines'])}")
        for pipeline in high_risk['pipelines'][:5]:
            print(f"  - {pipeline['id']}: Risk Score {pipeline['risk_score']}")
            print(f"    Age: {pipeline['age_years']:.1f} years, Material: {pipeline['material']}")
    
    if high_risk['meters']:
        print(f"\n⚠ High Risk Meters: {len(high_risk['meters'])}")
        for meter in high_risk['meters'][:5]:
            print(f"  - {meter['id']}: Issues - {', '.join(meter['issues'])}")
    
    # 6. Storage Tank Status
    print("\n6. Storage Tank Status")
    print("-" * 60)
    tank_status = monitoring_service.get_storage_tank_status()
    
    for tank in tank_status:
        print(f"\n{tank['name']} ({tank['id']})")
        print(f"  Capacity: {tank['capacity_liters']:,} L")
        print(f"  Current Level: {tank['current_level_liters']:,} L ({tank['fill_percentage']:.1f}%)")
        print(f"  Status: {tank['status']}")
        if tank.get('alert'):
            print(f"  ⚠ Alert: {tank['alert']}")
    
    # 7. Network Topology Overview
    print("\n7. Network Topology Overview")
    print("-" * 60)
    topology = monitoring_service.get_network_topology_overview()
    
    print(f"Total Network Length: {topology['total_length_km']:.2f} km")
    print(f"Pipeline Segments: {topology['total_segments']}")
    print(f"Connections: {topology['total_connections']}")
    print(f"Average Connectivity: {topology['avg_connectivity']:.2f}")
    print(f"Network Density: {topology['network_density']:.4f}")
    
    metrics = topology['connectivity_metrics']
    print(f"\nConnectivity Metrics:")
    print(f"  - Highly Connected: {metrics['highly_connected']} nodes")
    print(f"  - Isolated: {metrics['isolated']} nodes")
    print(f"  - Max Connections: {metrics['max_connections']}")
    
    print("\n" + "=" * 60)
    print("✓ Network monitoring demonstration completed!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
