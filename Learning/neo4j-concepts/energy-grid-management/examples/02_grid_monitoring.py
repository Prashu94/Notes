"""
Grid Monitoring Dashboard

Demonstrates real-time grid monitoring using the GridMonitoringService.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from connection import get_connection
from services import GridMonitoringService


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'=' * 80}")
    print(f" {title}")
    print(f"{'=' * 80}\n")


def main():
    """Run grid monitoring examples."""
    
    # Initialize connection and service
    conn = get_connection()
    
    try:
        # Verify connection
        if not conn.verify_connection():
            print("❌ Failed to connect to Neo4j")
            return
        
        print("✅ Connected to Neo4j")
        
        # Initialize service
        monitoring_service = GridMonitoringService()
        
        # Example 1: Overall Grid Health
        print_section("1. Overall Grid Health Status")
        health_status = monitoring_service.get_grid_health_status()
        print(f"Overall Status: {health_status['overall_status']}")
        print(f"Health Score: {health_status['health_score']}%")
        print(f"\nComponents:")
        print(f"  Power Plants:")
        print(f"    - Total: {health_status['components']['power_plants']['total']}")
        print(f"    - Operational: {health_status['components']['power_plants']['operational']}")
        print(f"    - Availability: {health_status['components']['power_plants']['availability_percent']}%")
        print(f"  Substations:")
        print(f"    - Total: {health_status['components']['substations']['total']}")
        print(f"    - Operational: {health_status['components']['substations']['operational']}")
        print(f"    - Availability: {health_status['components']['substations']['availability_percent']}%")
        print(f"\nCapacity:")
        print(f"  - Total Generation: {health_status['capacity']['total_generation_mw']:,.0f} MW")
        print(f"  - Total Transmission: {health_status['capacity']['total_transmission_mva']:,.0f} MVA")
        print(f"  - Renewable: {health_status['capacity']['renewable_percent']}%")
        
        # Example 2: Critical Components
        print_section("2. Critical Components Needing Attention")
        critical_components = monitoring_service.get_critical_components()
        print(f"Total Issues: {critical_components['total_issues']}")
        
        if critical_components['critical']:
            print(f"\n⚠️  CRITICAL Issues ({len(critical_components['critical'])}):")
            for item in critical_components['critical']:
                print(f"  - {item['type']}: {item['name']} - {item['issue']}")
        else:
            print("\n✅ No critical issues")
        
        if critical_components['warning']:
            print(f"\n⚡ WARNING Issues ({len(critical_components['warning'])}):")
            for item in critical_components['warning']:
                print(f"  - {item['type']}: {item['name']} - {item['issue']}")
        else:
            print("\n✅ No warnings")
        
        # Example 3: Renewable Energy Report
        print_section("3. Renewable Energy Report")
        renewable_report = monitoring_service.get_renewable_energy_report()
        print(f"Total Renewable Capacity: {renewable_report['summary']['total_renewable_capacity_mw']:,.0f} MW")
        print(f"Renewable Percentage: {renewable_report['summary']['renewable_percentage']}%")
        print(f"Number of Plants: {renewable_report['summary']['plant_count']}")
        print(f"\nBreakdown by Type:")
        for plant_type, data in renewable_report['by_type'].items():
            print(f"\n  {plant_type.upper()}:")
            print(f"    Count: {data['count']}")
            print(f"    Total Capacity: {data['total_capacity_mw']:,.0f} MW")
            print(f"    Plants:")
            for plant in data['plants']:
                print(f"      - {plant['name']}: {plant['capacity_mw']} MW ({plant['status']})")
        
        # Example 4: Regional Overview
        print_section("4. Regional Overview")
        regional_data = monitoring_service.get_regional_overview()
        for region in regional_data:
            print(f"\nRegion: {region['region']}")
            print(f"  Substations: {region['substations']}")
            print(f"  Capacity: {region['total_capacity']:,.0f} MVA")
            print(f"  Customers: {region['customers']}")
            print(f"  Consumption: {region['total_consumption']:,.0f} kWh")
            print(f"  Utilization: {region['utilization_percent']}%")
        
        # Example 5: Transmission Network Analysis
        print_section("5. Transmission Network Analysis")
        network_analysis = monitoring_service.analyze_transmission_network()
        if network_analysis.get('status') != 'NO_DATA':
            summary = network_analysis['summary']
            print(f"Total Lines: {summary['total_lines']}")
            print(f"Operational: {summary['operational_lines']}")
            print(f"Total Capacity: {summary['total_capacity_mw']:,.0f} MW")
            print(f"Total Distance: {summary['total_distance_km']:,.0f} km")
            print(f"Average Loss: {summary['average_loss_percent']:.2f}%")
            
            print(f"\nTop Capacity Lines:")
            for line in network_analysis['top_capacity_lines']:
                print(f"  - {line['line_id']}: {line['from']} → {line['to']}")
                print(f"    Capacity: {line['capacity_mw']} MW, Status: {line['status']}")
        
        # Example 6: Capacity Utilization
        print_section("6. System Capacity Utilization")
        utilization = monitoring_service.get_capacity_utilization()
        print(f"Status: {utilization['status']}")
        print(f"Total Capacity: {utilization['total_capacity_mw']:,.0f} MW")
        print(f"Current Consumption: {utilization['current_consumption_mw']:,.0f} MW")
        print(f"Utilization: {utilization['utilization_percent']:.2f}%")
        print(f"Available Headroom: {utilization['available_headroom_mw']:,.0f} MW")
        
        # Example 7: Customer Power Flow Check
        print_section("7. Customer Power Flow Analysis")
        # Get a sample customer
        from repositories import InfrastructureRepository
        infra_repo = InfrastructureRepository()
        customers = infra_repo.get_all_customers()
        
        if customers:
            sample_customer = customers[0]
            customer_id = sample_customer['id']
            customer_name = sample_customer['name']
            
            print(f"Analyzing power flow for: {customer_name} ({customer_id})")
            flow_status = monitoring_service.check_power_flow_to_customer(customer_id)
            
            print(f"\nStatus: {flow_status['status']}")
            print(f"Total Sources: {flow_status.get('total_sources', 0)}")
            print(f"Shortest Path: {flow_status.get('shortest_path_length', 'N/A')} hops")
            
            if 'sources_by_type' in flow_status:
                print(f"\nSources by Type:")
                for plant_type, sources in flow_status['sources_by_type'].items():
                    print(f"  {plant_type.upper()}: {len(sources)} plant(s)")
                    for source in sources[:3]:  # Show first 3
                        print(f"    - {source['plant_name']}: {source['capacity_mw']} MW ({source['path_length']} hops)")
        
    finally:
        conn.close()
        print("\n✅ Connection closed")


if __name__ == "__main__":
    main()
