"""
Script 4: Generate Synthetic Data
Generate additional synthetic data for testing and demonstrations.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.connection import Neo4jConnection
from src.models.incident import Incident, IncidentType, IncidentSeverity, IncidentStatus
from src.models.sensor import Sensor, SensorType, SensorStatus
from src.repositories.incident_repo import IncidentRepository
from src.repositories.sensor_repo import SensorRepository
from datetime import datetime, timedelta
import random


def generate_incidents(session, component_list: list, count: int = 20):
    """Generate synthetic incidents."""
    repo = IncidentRepository(session)
    
    incident_types = list(IncidentType)
    severities = list(IncidentSeverity)
    
    created = []
    
    for i in range(count):
        # Random time in past 90 days
        days_ago = random.randint(1, 90)
        reported_at = datetime.now() - timedelta(days=days_ago)
        
        # Random component
        component = random.choice(component_list)
        
        # Create incident
        incident = Incident(
            incident_id=f"INC-{datetime.now().strftime('%Y%m%d')}-{i:04d}",
            type=random.choice(incident_types),
            severity=random.choice(severities),
            status=IncidentStatus.RESOLVED if random.random() > 0.2 else IncidentStatus.IN_PROGRESS,
            description=f"Synthetic incident at {component['name']}",
            reported_at=reported_at,
            resolved_at=reported_at + timedelta(hours=random.randint(1, 24)) if random.random() > 0.2 else None,
            affected_customers=random.randint(0, 100),
            power_loss_mw=round(random.uniform(0, 50), 2)
        )
        
        incident_id = repo.create_incident(incident)
        repo.link_incident_to_component(incident_id, component['id'], component['type'])
        created.append(incident_id)
    
    return created


def generate_sensors(session, component_list: list, sensors_per_component: int = 2):
    """Generate synthetic sensors."""
    repo = SensorRepository(session)
    
    sensor_types = [SensorType.VOLTAGE, SensorType.CURRENT, SensorType.POWER, 
                    SensorType.TEMPERATURE, SensorType.FREQUENCY]
    
    created = []
    
    for component in component_list:
        for i in range(sensors_per_component):
            sensor_type = random.choice(sensor_types)
            
            # Type-specific thresholds
            if sensor_type == SensorType.VOLTAGE:
                current_val = random.uniform(110, 130)
                min_thresh = 115
                max_thresh = 125
                unit = "kV"
            elif sensor_type == SensorType.CURRENT:
                current_val = random.uniform(50, 150)
                min_thresh = 60
                max_thresh = 140
                unit = "A"
            elif sensor_type == SensorType.POWER:
                current_val = random.uniform(10, 100)
                min_thresh = 15
                max_thresh = 95
                unit = "MW"
            elif sensor_type == SensorType.TEMPERATURE:
                current_val = random.uniform(20, 80)
                min_thresh = 25
                max_thresh = 75
                unit = "°C"
            else:  # FREQUENCY
                current_val = random.uniform(59.8, 60.2)
                min_thresh = 59.9
                max_thresh = 60.1
                unit = "Hz"
            
            sensor = Sensor(
                sensor_id=f"SENS-{component['id']}-{sensor_type.value}-{i:02d}",
                name=f"{component['name']} {sensor_type.value.title()} Sensor {i+1}",
                type=sensor_type,
                status=SensorStatus.ACTIVE if random.random() > 0.1 else SensorStatus.FAULTY,
                location=component['name'],
                current_value=current_val,
                unit=unit,
                threshold_min=min_thresh,
                threshold_max=max_thresh,
                last_reading_at=datetime.now() - timedelta(minutes=random.randint(0, 60)),
                installed_at=datetime.now() - timedelta(days=random.randint(30, 365)),
                calibrated_at=datetime.now() - timedelta(days=random.randint(0, 90)),
                firmware_version=f"v{random.randint(1, 3)}.{random.randint(0, 9)}.{random.randint(0, 20)}"
            )
            
            sensor_id = repo.create_sensor(sensor)
            repo.link_sensor_to_component(sensor_id, component['id'], component['type'])
            created.append(sensor_id)
    
    return created


def main():
    print("\n" + "=" * 80)
    print("SYNTHETIC DATA GENERATION")
    print("=" * 80 + "\n")
    
    conn = Neo4jConnection()
    driver = conn.get_driver()
    
    if not driver:
        print("❌ Failed to connect to Neo4j")
        return
    
    try:
        with driver.session() as session:
            # Get existing components
            print("📋 Fetching existing components...")
            
            query = """
            MATCH (n)
            WHERE n:PowerPlant OR n:Substation OR n:TransmissionLine
            RETURN 
                n.id as id,
                n.name as name,
                labels(n)[0] as type
            LIMIT 50
            """
            
            result = session.run(query)
            components = [dict(r) for r in result]
            
            if not components:
                print("❌ No components found. Run data loading scripts first.")
                return
            
            print(f"✅ Found {len(components)} components\n")
            
            # Generate Incidents
            print("⚡ Generating incidents...")
            incident_count = int(input(f"  Number of incidents to generate (default 20): ") or "20")
            
            incidents = generate_incidents(session, components, incident_count)
            print(f"✅ Created {len(incidents)} incidents\n")
            
            # Generate Sensors
            print("📊 Generating sensors...")
            sensors_per = int(input(f"  Sensors per component (default 2): ") or "2")
            
            sensors = generate_sensors(session, components, sensors_per)
            print(f"✅ Created {len(sensors)} sensors\n")
            
            # Statistics
            print("=" * 80)
            print("GENERATION SUMMARY")
            print("=" * 80)
            
            # Incident stats
            incident_repo = IncidentRepository(session)
            stats = incident_repo.get_incident_statistics()
            
            print("\n📊 Incident Statistics:")
            print(f"  • Total Incidents: {stats.get('total_incidents', 0)}")
            print(f"  • Active Incidents: {stats.get('active_incidents', 0)}")
            print(f"  • Critical Incidents: {stats.get('critical_incidents', 0)}")
            print(f"  • Resolved Incidents: {stats.get('resolved_incidents', 0)}")
            print(f"  • Total Affected Customers: {stats.get('total_affected_customers', 0)}")
            print(f"  • Total Power Loss: {stats.get('total_power_loss_mw', 0):.2f} MW")
            
            # Sensor stats
            sensor_repo = SensorRepository(session)
            sensor_stats = sensor_repo.get_sensor_statistics()
            
            print("\n📡 Sensor Statistics:")
            print(f"  • Total Sensors: {sensor_stats.get('total_sensors', 0)}")
            print(f"  • Active Sensors: {sensor_stats.get('active_sensors', 0)}")
            print(f"  • Faulty Sensors: {sensor_stats.get('faulty_sensors', 0)}")
            print(f"  • Sensors in Alarm: {sensor_stats.get('in_alarm', 0)}")
            print(f"  • Stale Sensors (>1hr): {sensor_stats.get('stale_sensors', 0)}")
            
            # By type
            print("\n📈 By Sensor Type:")
            type_stats = sensor_repo.get_sensor_stats_by_type()
            for stat in type_stats:
                print(f"  • {stat['sensor_type']}: {stat['total']} sensors, "
                      f"{stat['active']} active, {stat['in_alarm']} in alarm")
            
            print("\n" + "=" * 80)
            print("✅ Synthetic data generation complete!")
            print("=" * 80 + "\n")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        conn.close()


if __name__ == "__main__":
    print("""
    This script generates synthetic incidents and sensors for testing.
    
    ⚠️  WARNING: This will add data to your Neo4j database.
    Make sure you're connected to a test environment.
    """)
    
    confirm = input("Continue? (yes/no): ").lower()
    if confirm == "yes":
        main()
    else:
        print("Aborted.")
