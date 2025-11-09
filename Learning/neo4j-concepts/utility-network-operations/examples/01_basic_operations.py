"""
Water Network Basic Operations

Demonstrates basic operations on water distribution network.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from connection import get_connection


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'=' * 80}")
    print(f" {title}")
    print(f"{'=' * 80}\n")


def main():
    """Run water network examples."""
    
    conn = get_connection()
    
    try:
        if not conn.verify_connection():
            print("❌ Failed to connect to Neo4j")
            return
        
        print("✅ Connected to Neo4j (Utility Network)")
        
        # Example 1: List all storage tanks
        print_section("1. Storage Tanks Overview")
        query = """
        MATCH (t:StorageTank)
        RETURN t.id as id, t.name as name, t.capacity_m3 as capacity,
               t.current_level_m3 as current_level, t.type as type,
               t.status as status
        ORDER BY t.capacity_m3 DESC
        """
        results = conn.execute_read(query)
        
        print(f"Total Storage Tanks: {len(results)}\n")
        for tank in results:
            fill_percent = (tank['current_level'] / tank['capacity'] * 100) if tank['capacity'] > 0 else 0
            print(f"Tank: {tank['name']} ({tank['type']})")
            print(f"  ID: {tank['id']}")
            print(f"  Capacity: {tank['capacity']:,.0f} m³")
            print(f"  Current Level: {tank['current_level']:,.0f} m³ ({fill_percent:.1f}%)")
            print(f"  Status: {tank['status']}")
            print()
        
        # Example 2: Pumping stations
        print_section("2. Pumping Stations")
        query = """
        MATCH (ps:PumpingStation)
        RETURN ps.id as id, ps.name as name,
               ps.capacity_m3_per_hour as capacity,
               ps.power_consumption_kw as power,
               ps.num_pumps as num_pumps,
               ps.efficiency_percent as efficiency,
               ps.status as status
        ORDER BY ps.capacity_m3_per_hour DESC
        """
        results = conn.execute_read(query)
        
        print(f"Total Pumping Stations: {len(results)}\n")
        for station in results:
            print(f"Station: {station['name']}")
            print(f"  Capacity: {station['capacity']:,.0f} m³/h")
            print(f"  Power: {station['power']} kW")
            print(f"  Pumps: {station['num_pumps']}")
            print(f"  Efficiency: {station['efficiency']}%")
            print(f"  Status: {station['status']}")
            print()
        
        # Example 3: Pipeline network
        print_section("3. Pipeline Network")
        query = """
        MATCH (p:Pipeline)
        RETURN p.id as id, p.name as name,
               p.diameter_mm as diameter, p.length_m as length,
               p.material as material,
               p.flow_rate_m3_per_hour as flow_rate,
               p.status as status
        ORDER BY p.diameter_mm DESC, p.length_m DESC
        """
        results = conn.execute_read(query)
        
        total_length = sum(p['length'] for p in results)
        print(f"Total Pipelines: {len(results)}")
        print(f"Total Length: {total_length:,.0f} meters ({total_length/1000:.2f} km)\n")
        
        for pipe in results:
            print(f"Pipeline: {pipe['name']}")
            print(f"  Diameter: {pipe['diameter']} mm")
            print(f"  Length: {pipe['length']:,.0f} m")
            print(f"  Material: {pipe['material']}")
            print(f"  Flow Rate: {pipe['flow_rate']} m³/h")
            print(f"  Status: {pipe['status']}")
            print()
        
        # Example 4: Water flow from source to customers
        print_section("4. Water Flow Tracing")
        query = """
        MATCH path = (source:StorageTank)-[:SUPPLIES|CONNECTS_TO*1..10]->(customer:Customer)
        WITH source, customer, 
             length(path) as hops,
             [node in nodes(path) | labels(node)[0] + ': ' + node.name] as route
        RETURN source.name as source_name,
               customer.name as customer_name,
               customer.type as customer_type,
               hops,
               route
        ORDER BY hops, customer_name
        LIMIT 15
        """
        results = conn.execute_read(query)
        
        print(f"Sample Water Flow Paths (first 15):\n")
        for i, path in enumerate(results, 1):
            print(f"{i}. {path['source_name']} → {path['customer_name']} ({path['customer_type']})")
            print(f"   Hops: {path['hops']}")
            print(f"   Route: {' → '.join(path['route'][:4])}{'...' if len(path['route']) > 4 else ''}")
            print()
        
        # Example 5: Sensor monitoring
        print_section("5. IoT Sensor Monitoring")
        query = """
        MATCH (s:Sensor)-[r:MONITORS]->(target)
        RETURN s.id as sensor_id, s.type as sensor_type,
               labels(target)[0] as monitoring,
               target.name as target_name,
               r.measurement_type as measurement,
               r.last_reading as last_reading,
               r.unit as unit,
               s.status as status
        ORDER BY sensor_type, target_name
        """
        results = conn.execute_read(query)
        
        print(f"Active Sensors: {len(results)}\n")
        
        # Group by sensor type
        by_type = {}
        for sensor in results:
            stype = sensor['sensor_type']
            if stype not in by_type:
                by_type[stype] = []
            by_type[stype].append(sensor)
        
        for stype, sensors in by_type.items():
            print(f"{stype.upper()} Sensors: {len(sensors)}")
            for sensor in sensors:
                print(f"  {sensor['sensor_id']}: Monitoring {sensor['monitoring']} - {sensor['target_name']}")
                print(f"    Last Reading: {sensor['last_reading']} {sensor['unit']}")
                print(f"    Status: {sensor['status']}")
            print()
        
        # Example 6: Customer consumption analysis
        print_section("6. Customer Consumption Analysis")
        query = """
        MATCH (c:Customer)
        WITH c.type as customer_type,
             count(c) as customer_count,
             sum(c.average_consumption_m3) as total_consumption,
             avg(c.average_consumption_m3) as avg_consumption,
             max(c.average_consumption_m3) as max_consumption
        RETURN customer_type, customer_count, total_consumption,
               round(avg_consumption, 2) as avg_consumption,
               max_consumption
        ORDER BY total_consumption DESC
        """
        results = conn.execute_read(query)
        
        print("Consumption by Customer Type:\n")
        for result in results:
            print(f"{result['customer_type'].upper()}:")
            print(f"  Customers: {result['customer_count']}")
            print(f"  Total Consumption: {result['total_consumption']:,.0f} m³/month")
            print(f"  Average per Customer: {result['avg_consumption']:,.2f} m³/month")
            print(f"  Highest Consumer: {result['max_consumption']:,.0f} m³/month")
            print()
        
        # Example 7: Smart meter data
        print_section("7. Smart Meter Readings")
        query = """
        MATCH (m:SmartMeter)-[r:MEASURES]->(c:Customer)
        RETURN m.id as meter_id, m.model as model,
               m.reading_m3 as reading,
               m.flow_rate_m3_per_hour as flow_rate,
               c.name as customer_name,
               c.type as customer_type,
               m.status as status
        ORDER BY reading DESC
        LIMIT 10
        """
        results = conn.execute_read(query)
        
        print("Top 10 Smart Meter Readings:\n")
        for i, meter in enumerate(results, 1):
            print(f"{i}. Customer: {meter['customer_name']} ({meter['customer_type']})")
            print(f"   Meter: {meter['meter_id']} ({meter['model']})")
            print(f"   Reading: {meter['reading']:,.2f} m³")
            print(f"   Current Flow: {meter['flow_rate']} m³/h")
            print(f"   Status: {meter['status']}")
            print()
        
        # Example 8: Network health check
        print_section("8. Network Health Summary")
        query = """
        MATCH (t:StorageTank)
        WITH count(t) as total_tanks,
             sum(CASE WHEN t.status = 'operational' THEN 1 ELSE 0 END) as operational_tanks,
             sum(t.capacity_m3) as total_capacity,
             sum(t.current_level_m3) as current_level
        MATCH (ps:PumpingStation)
        WITH total_tanks, operational_tanks, total_capacity, current_level,
             count(ps) as total_pumps,
             sum(CASE WHEN ps.status = 'operational' THEN 1 ELSE 0 END) as operational_pumps
        MATCH (p:Pipeline)
        WITH total_tanks, operational_tanks, total_capacity, current_level,
             total_pumps, operational_pumps,
             count(p) as total_pipes,
             sum(CASE WHEN p.status = 'operational' THEN 1 ELSE 0 END) as operational_pipes,
             sum(p.length_m) as total_pipe_length
        MATCH (c:Customer)
        RETURN total_tanks, operational_tanks, total_capacity, current_level,
               total_pumps, operational_pumps,
               total_pipes, operational_pipes, total_pipe_length,
               count(c) as total_customers
        """
        results = conn.execute_read(query)
        
        if results:
            data = results[0]
            fill_percent = (data['current_level'] / data['total_capacity'] * 100) if data['total_capacity'] > 0 else 0
            tank_availability = (data['operational_tanks'] / data['total_tanks'] * 100) if data['total_tanks'] > 0 else 0
            pump_availability = (data['operational_pumps'] / data['total_pumps'] * 100) if data['total_pumps'] > 0 else 0
            pipe_availability = (data['operational_pipes'] / data['total_pipes'] * 100) if data['total_pipes'] > 0 else 0
            
            print("Network Status:")
            print(f"\nStorage:")
            print(f"  Tanks: {data['operational_tanks']}/{data['total_tanks']} operational ({tank_availability:.1f}%)")
            print(f"  Total Capacity: {data['total_capacity']:,.0f} m³")
            print(f"  Current Level: {data['current_level']:,.0f} m³ ({fill_percent:.1f}%)")
            
            print(f"\nInfrastructure:")
            print(f"  Pumping Stations: {data['operational_pumps']}/{data['total_pumps']} operational ({pump_availability:.1f}%)")
            print(f"  Pipelines: {data['operational_pipes']}/{data['total_pipes']} operational ({pipe_availability:.1f}%)")
            print(f"  Total Pipeline Length: {data['total_pipe_length']:,.0f} m ({data['total_pipe_length']/1000:.2f} km)")
            
            print(f"\nService:")
            print(f"  Total Customers: {data['total_customers']}")
            
            # Overall health score
            avg_availability = (tank_availability + pump_availability + pipe_availability) / 3
            print(f"\nOverall Health Score: {avg_availability:.1f}%")
            if avg_availability >= 95:
                print("Status: ✅ HEALTHY")
            elif avg_availability >= 85:
                print("Status: ⚠️  WARNING")
            else:
                print("Status: ❌ CRITICAL")
        
    finally:
        conn.close()
        print("\n✅ Connection closed")


if __name__ == "__main__":
    main()
