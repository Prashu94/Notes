"""
Load Forecasting and Analytics

Demonstrates analyzing consumption patterns and forecasting future load.
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from connection import get_connection


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'=' * 80}")
    print(f" {title}")
    print(f"{'=' * 80}\n")


def main():
    """Run load forecasting examples."""
    
    conn = get_connection()
    
    try:
        if not conn.verify_connection():
            print("❌ Failed to connect to Neo4j")
            return
        
        print("✅ Connected to Neo4j")
        
        # Example 1: Customer Consumption Analysis
        print_section("1. Customer Consumption Analysis")
        query = """
        MATCH (c:Customer)
        WITH c.type as customer_type,
             count(c) as customer_count,
             sum(c.average_consumption_kwh) as total_consumption,
             avg(c.average_consumption_kwh) as avg_consumption,
             max(c.average_consumption_kwh) as max_consumption,
             min(c.average_consumption_kwh) as min_consumption
        RETURN customer_type, customer_count, total_consumption,
               round(avg_consumption, 2) as avg_consumption,
               max_consumption, min_consumption
        ORDER BY total_consumption DESC
        """
        results = conn.execute_read(query)
        
        print("Consumption by Customer Type:\n")
        total_all = sum(r['total_consumption'] for r in results)
        
        for result in results:
            pct = (result['total_consumption'] / total_all * 100) if total_all > 0 else 0
            print(f"{result['customer_type'].upper()}:")
            print(f"  Customers: {result['customer_count']}")
            print(f"  Total Consumption: {result['total_consumption']:,.0f} kWh ({pct:.1f}%)")
            print(f"  Average per Customer: {result['avg_consumption']:,.0f} kWh")
            print(f"  Range: {result['min_consumption']:,.0f} - {result['max_consumption']:,.0f} kWh")
            print()
        
        # Example 2: Peak Load Analysis by Substation
        print_section("2. Peak Load Analysis by Substation")
        query = """
        MATCH (s:Substation)-[:SUPPLIES_POWER]->(c:Customer)
        WITH s, 
             count(c) as customer_count,
             sum(c.average_consumption_kwh) as total_load_kwh,
             s.capacity_mva as capacity_mva
        WITH s, customer_count, total_load_kwh, capacity_mva,
             (total_load_kwh / 1000.0) as estimated_load_mw,
             capacity_mva * 0.8 as usable_capacity_mw
        RETURN s.id as substation_id, s.name as substation_name,
               s.type as substation_type, customer_count,
               round(estimated_load_mw, 2) as estimated_load_mw,
               round(usable_capacity_mw, 2) as capacity_mw,
               round(100.0 * estimated_load_mw / usable_capacity_mw, 2) as utilization_percent,
               CASE 
                   WHEN estimated_load_mw > usable_capacity_mw THEN 'OVERLOADED'
                   WHEN estimated_load_mw > usable_capacity_mw * 0.9 THEN 'CRITICAL'
                   WHEN estimated_load_mw > usable_capacity_mw * 0.8 THEN 'WARNING'
                   ELSE 'NORMAL'
               END as status
        ORDER BY utilization_percent DESC
        """
        results = conn.execute_read(query)
        
        print("Substation Load Analysis:\n")
        for sub in results:
            print(f"{sub['substation_name']} ({sub['substation_type']})")
            print(f"  Customers: {sub['customer_count']}")
            print(f"  Estimated Load: {sub['estimated_load_mw']} MW")
            print(f"  Capacity: {sub['capacity_mw']} MW")
            print(f"  Utilization: {sub['utilization_percent']}%")
            print(f"  Status: {sub['status']}")
            print()
        
        # Example 3: Regional Load Distribution
        print_section("3. Regional Load Distribution")
        query = """
        MATCH (s:Substation)-[:SUPPLIES_POWER]->(c:Customer)
        WITH s.region as region,
             count(DISTINCT s) as substations,
             count(DISTINCT c) as customers,
             sum(c.average_consumption_kwh) as total_consumption,
             sum(s.capacity_mva) as total_capacity
        RETURN region, substations, customers,
               round(total_consumption, 2) as total_consumption_kwh,
               round(total_capacity, 2) as total_capacity_mva,
               round(total_consumption / 1000.0, 2) as estimated_load_mw,
               round(total_capacity * 0.8, 2) as usable_capacity_mw
        ORDER BY total_consumption DESC
        """
        results = conn.execute_read(query)
        
        print("Regional Load Distribution:\n")
        for region in results:
            load_mw = region['estimated_load_mw']
            capacity_mw = region['usable_capacity_mw']
            utilization = (load_mw / capacity_mw * 100) if capacity_mw > 0 else 0
            
            print(f"Region: {region['region']}")
            print(f"  Substations: {region['substations']}, Customers: {region['customers']}")
            print(f"  Total Consumption: {region['total_consumption_kwh']:,.0f} kWh")
            print(f"  Estimated Load: {load_mw} MW")
            print(f"  Available Capacity: {capacity_mw} MW")
            print(f"  Utilization: {utilization:.2f}%")
            print()
        
        # Example 4: Growth Projection
        print_section("4. Load Growth Projection (5-Year Forecast)")
        query = """
        MATCH (c:Customer)
        WITH c.type as customer_type,
             sum(c.average_consumption_kwh) as current_load
        RETURN customer_type, current_load
        """
        results = conn.execute_read(query)
        
        # Assume different growth rates by customer type
        growth_rates = {
            'residential': 0.03,    # 3% annual growth
            'commercial': 0.05,     # 5% annual growth
            'industrial': 0.02      # 2% annual growth
        }
        
        print("5-Year Load Growth Forecast:\n")
        print(f"{'Year':<8} {'Residential (MW)':<20} {'Commercial (MW)':<20} {'Industrial (MW)':<20} {'Total (MW)':<15}")
        print("-" * 83)
        
        for year in range(6):
            year_label = "Current" if year == 0 else f"Year {year}"
            row_data = [year_label]
            year_total = 0
            
            for result in results:
                ctype = result['customer_type']
                current = result['current_load'] / 1000.0  # Convert to MW
                growth_rate = growth_rates.get(ctype, 0.03)
                projected = current * ((1 + growth_rate) ** year)
                row_data.append(f"{projected:,.1f}")
                year_total += projected
            
            row_data.append(f"{year_total:,.1f}")
            print(f"{row_data[0]:<8} {row_data[1]:<20} {row_data[2]:<20} {row_data[3]:<20} {row_data[4]:<15}")
        
        # Example 5: Capacity Planning Recommendations
        print_section("5. Capacity Planning Recommendations")
        query = """
        MATCH (s:Substation)
        OPTIONAL MATCH (s)-[:SUPPLIES_POWER]->(c:Customer)
        WITH s, 
             coalesce(sum(c.average_consumption_kwh), 0) as current_load_kwh,
             s.capacity_mva as capacity_mva
        WITH s, current_load_kwh, capacity_mva,
             (current_load_kwh / 1000.0) as current_load_mw,
             capacity_mva * 0.8 as usable_capacity_mw,
             (current_load_kwh / 1000.0) * 1.25 as projected_load_5yr_mw
        WHERE projected_load_5yr_mw > usable_capacity_mw
        RETURN s.id as substation_id, s.name as substation_name,
               s.region as region,
               round(current_load_mw, 2) as current_load_mw,
               round(projected_load_5yr_mw, 2) as projected_load_mw,
               round(usable_capacity_mw, 2) as current_capacity_mw,
               round(projected_load_5yr_mw - usable_capacity_mw, 2) as capacity_gap_mw
        ORDER BY capacity_gap_mw DESC
        """
        results = conn.execute_read(query)
        
        if results:
            print("Substations Requiring Capacity Upgrades:\n")
            for sub in results:
                print(f"⚠️  {sub['substation_name']} ({sub['region']})")
                print(f"    Current Load: {sub['current_load_mw']} MW")
                print(f"    Projected 5-Year Load: {sub['projected_load_mw']} MW")
                print(f"    Current Capacity: {sub['current_capacity_mw']} MW")
                print(f"    Capacity Gap: {sub['capacity_gap_mw']} MW")
                print(f"    Recommended Action: Upgrade capacity by at least {sub['capacity_gap_mw']} MW")
                print()
        else:
            print("✅ All substations have sufficient capacity for projected 5-year growth")
        
        # Example 6: High-Value Customer Analysis
        print_section("6. High-Value Customer Analysis")
        query = """
        MATCH (c:Customer)
        WITH c, c.average_consumption_kwh as consumption
        ORDER BY consumption DESC
        LIMIT 10
        MATCH (c)<-[:SUPPLIES_POWER]-(s:Substation)
        OPTIONAL MATCH path = (p:PowerPlant)-[:GENERATES]->()
                              -[:TRANSMITS_TO*]->()-[:SUPPLIES_POWER]->(c)
        WITH c, consumption, s,
             count(DISTINCT p) as power_sources
        RETURN c.id as customer_id, c.name as customer_name,
               c.type as customer_type, consumption,
               s.name as serving_substation, power_sources
        ORDER BY consumption DESC
        """
        results = conn.execute_read(query)
        
        print("Top 10 Highest Consumption Customers:\n")
        for i, customer in enumerate(results, 1):
            print(f"{i}. {customer['customer_name']} ({customer['customer_type']})")
            print(f"   Consumption: {customer['consumption']:,.0f} kWh")
            print(f"   Served by: {customer['serving_substation']}")
            print(f"   Power Sources: {customer['power_sources']}")
            print()
        
    finally:
        conn.close()
        print("\n✅ Connection closed")


if __name__ == "__main__":
    main()
