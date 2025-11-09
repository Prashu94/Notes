"""
Example 7: Real-Time Grid Monitoring
Demonstrates real-time monitoring capabilities with sensors and incidents.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.connection import Neo4jConnection
from src.services.grid_monitoring import GridMonitoringService
from src.services.outage_management import OutageManagementService
from src.repositories.sensor_repo import SensorRepository
from src.models.incident import IncidentType, IncidentSeverity
from datetime import datetime
import time


def print_dashboard(title: str):
    print(f"\n{'#' * 80}")
    print(f"#{title:^78}#")
    print(f"{'#' * 80}\n")


def main():
    conn = Neo4jConnection()
    driver = conn.get_driver()
    
    if not driver:
        print("Failed to connect to Neo4j")
        return
    
    try:
        grid_service = GridMonitoringService(driver)
        outage_service = OutageManagementService(driver)
        
        # Dashboard Loop (simulating real-time)
        for iteration in range(1, 4):  # 3 iterations
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            print_dashboard(f"GRID MONITORING DASHBOARD - {timestamp}")
            
            # 1. Grid Health Status
            print("🏥 GRID HEALTH STATUS")
            print("-" * 80)
            health = grid_service.get_grid_health_status()
            
            print(f"Overall Health Score: {health['overall_health_score']:.1f}%")
            print(f"  • Plants Operational: {health['operational_plants']}/{health['total_plants']}")
            print(f"  • Substations Operational: {health['operational_substations']}/{health['total_substations']}")
            print(f"  • Lines Active: {health['active_lines']}/{health['total_lines']}")
            print(f"  • Available Capacity: {health['available_capacity']:.0f} MW / "
                  f"{health['total_capacity']:.0f} MW")
            
            # 2. Active Outages
            print(f"\n⚡ ACTIVE OUTAGES")
            print("-" * 80)
            outages = outage_service.get_active_outages()
            
            if outages:
                print(f"Total Active Outages: {len(outages)}\n")
                for outage in outages[:5]:
                    severity_icon = "🔴" if outage['severity'] == 'critical' else "🟡"
                    print(f"{severity_icon} {outage['incident_id']} - {outage['incident_type'].upper()}")
                    print(f"   Component: {outage['component_name']} ({outage['component_type']})")
                    print(f"   Location: {outage['location']}")
                    print(f"   Severity: {outage['severity'].upper()}")
                    print(f"   Affected Customers: {outage['affected_customers']}")
                    print(f"   Power Loss: {outage['power_loss_mw']:.1f} MW")
                    print()
            else:
                print("✅ No active outages\n")
            
            # 3. Critical Components
            print("⚠️  CRITICAL COMPONENTS")
            print("-" * 80)
            critical = grid_service.get_critical_components()
            
            if critical['total_critical'] > 0:
                print(f"Components requiring attention: {critical['total_critical']}\n")
                
                if critical.get('overloaded_substations'):
                    print("Overloaded Substations:")
                    for sub in critical['overloaded_substations'][:3]:
                        print(f"  • {sub['name']}: {sub['utilization_pct']:.0f}% utilization")
                
                if critical.get('high_loss_lines'):
                    print("\nHigh Loss Transmission Lines:")
                    for line in critical['high_loss_lines'][:3]:
                        print(f"  • {line['name']}: {line['loss_percent']:.1f}% loss")
                
                if critical.get('maintenance_components'):
                    print("\nComponents Under Maintenance:")
                    for comp in critical['maintenance_components'][:3]:
                        print(f"  • {comp['name']} ({comp['type']})")
            else:
                print("✅ All components operating normally\n")
            
            # 4. Sensor Monitoring
            print("📊 SENSOR STATUS")
            print("-" * 80)
            with driver.session() as session:
                sensor_repo = SensorRepository(session)
                
                stats = sensor_repo.get_sensor_statistics()
                alarms = sensor_repo.get_sensors_in_alarm()
                
                print(f"Total Sensors: {stats['total_sensors']}")
                print(f"  • Active: {stats['active_sensors']}")
                print(f"  • In Alarm: {stats['in_alarm']}")
                print(f"  • Faulty: {stats['faulty_sensors']}")
                print(f"  • Stale (>1hr): {stats['stale_sensors']}")
                
                if alarms:
                    print(f"\n🚨 Active Alarms ({len(alarms)}):")
                    for sensor in alarms[:5]:
                        alarm_type = "HIGH" if sensor.current_value > sensor.threshold_max else "LOW"
                        print(f"  • {sensor.name} ({sensor.type.value}): {sensor.current_value:.2f} {sensor.unit}")
                        print(f"    {alarm_type} - Threshold: {sensor.threshold_min}-{sensor.threshold_max}")
                else:
                    print("\n✅ No sensor alarms")
            
            # 5. Renewable Energy
            print(f"\n🌱 RENEWABLE ENERGY STATUS")
            print("-" * 80)
            renewable = grid_service.get_renewable_energy_report()
            
            print(f"Total Renewable Capacity: {renewable['total_renewable_capacity']:.0f} MW")
            print(f"Renewable Percentage: {renewable['renewable_percentage']:.1f}%")
            print(f"  • Solar: {renewable['by_type'].get('solar', 0):.0f} MW")
            print(f"  • Wind: {renewable['by_type'].get('wind', 0):.0f} MW")
            print(f"  • Hydro: {renewable['by_type'].get('hydro', 0):.0f} MW")
            
            # 6. Regional Overview
            print(f"\n🗺️  REGIONAL OVERVIEW")
            print("-" * 80)
            regional = grid_service.get_regional_overview()
            
            for region in regional[:3]:
                print(f"\n{region['region']} ({region['state']}):")
                print(f"  Capacity: {region['total_capacity']:.0f} MW")
                print(f"  Load: {region['total_consumption']:.0f} MW")
                print(f"  Utilization: {region['utilization_pct']:.1f}%")
                print(f"  Customers: {region['customer_count']}")
            
            # 7. Transmission Network Health
            print(f"\n🔌 TRANSMISSION NETWORK")
            print("-" * 80)
            transmission = grid_service.analyze_transmission_network()
            
            print(f"Total Lines: {transmission['total_lines']}")
            print(f"Active Lines: {transmission['active_lines']} ({transmission['availability_pct']:.1f}%)")
            print(f"Average Loss: {transmission['avg_loss_percent']:.2f}%")
            print(f"Total Capacity: {transmission['total_capacity_mw']:.0f} MW")
            
            if transmission.get('high_loss_lines'):
                print(f"\nHigh Loss Lines ({len(transmission['high_loss_lines'])}):")
                for line in transmission['high_loss_lines'][:3]:
                    print(f"  • {line['name']}: {line['loss_percent']:.1f}% loss")
            
            # 8. Capacity Utilization
            print(f"\n📈 CAPACITY UTILIZATION")
            print("-" * 80)
            capacity = grid_service.get_capacity_utilization()
            
            print(f"Generation: {capacity['generation_utilization_pct']:.1f}%")
            print(f"  Capacity: {capacity['total_capacity_mw']:.0f} MW")
            print(f"  Load: {capacity['total_load_mw']:.0f} MW")
            print(f"  Reserve: {capacity['reserve_capacity_mw']:.0f} MW ({capacity['reserve_margin_pct']:.1f}%)")
            
            # Pause between iterations (simulation)
            if iteration < 3:
                print(f"\n{'─' * 80}")
                print(f"Refreshing dashboard in 3 seconds...")
                print(f"{'─' * 80}")
                time.sleep(3)
        
        # Final Summary
        print_dashboard("MONITORING SESSION COMPLETE")
        
        dashboard = outage_service.get_outage_dashboard()
        stats = dashboard['statistics']
        
        print("📊 SESSION SUMMARY:")
        print(f"  • Total Incidents: {stats.get('total_incidents', 0)}")
        print(f"  • Active Incidents: {stats.get('active_incidents', 0)}")
        print(f"  • Critical Incidents: {stats.get('critical_incidents', 0)}")
        print(f"  • Affected Customers: {stats.get('total_affected_customers', 0)}")
        print(f"  • Power Loss: {stats.get('total_power_loss_mw', 0):.0f} MW")
        
    finally:
        conn.close()


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("REAL-TIME GRID MONITORING SYSTEM")
    print("=" * 80)
    main()
    print("\n" + "=" * 80)
    print("Monitoring Complete!")
    print("=" * 80 + "\n")
