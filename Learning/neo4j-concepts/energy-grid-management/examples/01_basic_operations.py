#!/usr/bin/env python3
"""
Example 1: Basic Operations

This script demonstrates basic CRUD operations and queries
for the energy grid management system.
"""

import sys
from pathlib import Path
from datetime import date, datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.connection import get_connection, close_connection


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def example_1_read_power_plants():
    """Example: Read all power plants."""
    print_section("1. Read All Power Plants")
    
    query = """
    MATCH (p:PowerPlant)
    RETURN p.id, p.name, p.type, p.capacity_mw, p.status
    ORDER BY p.capacity_mw DESC
    """
    
    conn = get_connection()
    results = conn.execute_read(query)
    
    print(f"\nFound {len(results)} power plants:\n")
    for r in results:
        print(f"• {r['p.name']:30} | {r['p.type']:12} | {r['p.capacity_mw']:8.1f} MW | {r['p.status']}")


def example_2_power_flow_tracing():
    """Example: Trace power flow from plant to customer."""
    print_section("2. Trace Power Flow from Generation to Consumption")
    
    query = """
    MATCH path = (plant:PowerPlant {id: 'PP-001'})-[:GENERATES]->()
                 -[:TRANSMITS_TO*0..3]->()-[:SUPPLIES_POWER]->(customer:Customer)
    RETURN 
        plant.name as power_plant,
        customer.name as customer,
        customer.type as customer_type,
        length(path) as hops
    ORDER BY hops, customer.name
    LIMIT 10
    """
    
    conn = get_connection()
    results = conn.execute_read(query)
    
    print(f"\nPower flow from Riverside Nuclear Plant:\n")
    for r in results:
        print(f"• {r['power_plant']:30} → {r['customer']:30} ({r['customer_type']}) - {r['hops']} hops")


def example_3_find_critical_substations():
    """Example: Find substations with highest capacity."""
    print_section("3. Find Critical Substations")
    
    query = """
    MATCH (s:Substation)
    OPTIONAL MATCH (s)-[:SUPPLIES_POWER]->(c:Customer)
    RETURN 
        s.name as substation,
        s.voltage_kv as voltage,
        s.capacity_mva as capacity,
        s.region as region,
        count(c) as customers_served
    ORDER BY s.capacity_mva DESC
    LIMIT 10
    """
    
    conn = get_connection()
    results = conn.execute_read(query)
    
    print(f"\nTop 10 Critical Substations:\n")
    for r in results:
        print(f"• {r['substation']:30} | {r['voltage']:6.0f} kV | "
              f"{r['capacity']:8.1f} MVA | Serves {r['customers_served']} customers | {r['region']}")


def example_4_customer_by_consumption():
    """Example: Find customers by consumption level."""
    print_section("4. Customers by Consumption Level")
    
    query = """
    MATCH (c:Customer)
    RETURN 
        c.name as customer,
        c.type as type,
        c.average_consumption_kwh as consumption,
        c.peak_demand_kw as peak_demand,
        c.region as region
    ORDER BY c.average_consumption_kwh DESC
    LIMIT 10
    """
    
    conn = get_connection()
    results = conn.execute_read(query)
    
    print(f"\nTop 10 Consumers:\n")
    for r in results:
        print(f"• {r['customer']:30} | {r['type']:12} | "
              f"{r['consumption']:10,.0f} kWh/mo | Peak: {r['peak_demand']:6.0f} kW | {r['region']}")


def example_5_transmission_network():
    """Example: Analyze transmission network."""
    print_section("5. Transmission Network Analysis")
    
    query = """
    MATCH (s1:Substation)-[t:TRANSMITS_TO]->(s2:Substation)
    RETURN 
        s1.name as from_substation,
        s2.name as to_substation,
        t.capacity_mw as capacity,
        t.distance_km as distance,
        t.loss_percent as loss,
        t.status as status
    ORDER BY t.capacity_mw DESC
    """
    
    conn = get_connection()
    results = conn.execute_read(query)
    
    print(f"\nTransmission Lines:\n")
    for r in results:
        print(f"• {r['from_substation']:30} → {r['to_substation']:30}")
        print(f"  Capacity: {r['capacity']:6.0f} MW | Distance: {r['distance']:6.1f} km | "
              f"Loss: {r['loss']:.1f}% | Status: {r['status']}")


def example_6_regional_capacity():
    """Example: Calculate regional generation capacity."""
    print_section("6. Regional Generation Capacity")
    
    query = """
    MATCH (p:PowerPlant)-[:GENERATES]->(s:Substation)
    RETURN 
        s.region as region,
        count(DISTINCT p) as num_plants,
        collect(DISTINCT p.type) as plant_types,
        sum(p.capacity_mw) as total_capacity,
        avg(p.capacity_mw) as avg_capacity
    ORDER BY total_capacity DESC
    """
    
    conn = get_connection()
    results = conn.execute_read(query)
    
    print(f"\nGeneration Capacity by Region:\n")
    for r in results:
        print(f"\n• {r['region']} Region:")
        print(f"  Plants: {r['num_plants']}")
        print(f"  Types: {', '.join(r['plant_types'])}")
        print(f"  Total Capacity: {r['total_capacity']:,.0f} MW")
        print(f"  Average Capacity: {r['avg_capacity']:,.0f} MW")


def example_7_renewable_percentage():
    """Example: Calculate renewable energy percentage."""
    print_section("7. Renewable Energy Mix")
    
    query = """
    MATCH (p:PowerPlant)
    WITH p, 
         CASE WHEN p.type IN ['solar', 'wind', 'hydro'] THEN 'renewable' ELSE 'non-renewable' END as category
    RETURN 
        category,
        collect(p.type) as types,
        count(p) as num_plants,
        sum(p.capacity_mw) as total_capacity,
        round(100.0 * sum(p.capacity_mw) / 
              (SELECT sum(capacity_mw) FROM (MATCH (all:PowerPlant) RETURN all)), 2) as percentage
    ORDER BY total_capacity DESC
    """
    
    conn = get_connection()
    results = conn.execute_read(query)
    
    print(f"\nEnergy Mix Analysis:\n")
    for r in results:
        print(f"\n• {r['category'].title()}:")
        print(f"  Types: {', '.join(set(r['types']))}")
        print(f"  Plants: {r['num_plants']}")
        print(f"  Total Capacity: {r['total_capacity']:,.0f} MW")
        print(f"  Percentage: {r['percentage']:.1f}%")


def main():
    """Run all examples."""
    print("\n" + "=" * 70)
    print("  ENERGY GRID MANAGEMENT - BASIC OPERATIONS DEMO")
    print("=" * 70)
    
    try:
        # Verify connection
        conn = get_connection()
        if not conn.verify_connection():
            print("\n✗ Error: Could not connect to Neo4j")
            print("  Make sure Neo4j is running and credentials are correct")
            sys.exit(1)
        
        print("\n✓ Connected to Neo4j successfully")
        
        # Check if data exists
        node_count = conn.get_node_count()
        if node_count == 0:
            print("\n⚠ Warning: Database is empty")
            print("  Run './scripts/02_load_sample_data.py' first")
            sys.exit(1)
        
        print(f"✓ Database contains {node_count} nodes\n")
        
        # Run examples
        example_1_read_power_plants()
        example_2_power_flow_tracing()
        example_3_find_critical_substations()
        example_4_customer_by_consumption()
        example_5_transmission_network()
        example_6_regional_capacity()
        example_7_renewable_percentage()
        
        print("\n" + "=" * 70)
        print("  All examples completed successfully!")
        print("=" * 70 + "\n")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    finally:
        close_connection()


if __name__ == "__main__":
    main()
