"""
Graph Algorithms for Energy Grid Analysis

Demonstrates shortest path, centrality, and network analysis algorithms.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from connection import get_connection
from repositories import InfrastructureRepository


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'=' * 80}")
    print(f" {title}")
    print(f"{'=' * 80}\n")


def main():
    """Run graph algorithm examples."""
    
    conn = get_connection()
    
    try:
        if not conn.verify_connection():
            print("❌ Failed to connect to Neo4j")
            return
        
        print("✅ Connected to Neo4j")
        infra_repo = InfrastructureRepository()
        
        # Example 1: Shortest Path Between Substations
        print_section("1. Shortest Path Analysis")
        substations = infra_repo.get_all_substations()
        
        if len(substations) >= 2:
            sub1 = substations[0]
            sub2 = substations[-1]
            
            print(f"Finding shortest path:")
            print(f"  From: {sub1['name']} ({sub1['id']})")
            print(f"  To: {sub2['name']} ({sub2['id']})")
            
            path_result = infra_repo.get_shortest_path_between_substations(
                sub1['id'], sub2['id']
            )
            
            if path_result:
                print(f"\nRoute ({path_result['hops']} hops):")
                for i, node_name in enumerate(path_result['route'], 1):
                    print(f"  {i}. {node_name}")
                print(f"\nTotal Distance: {path_result['total_distance_km']:.2f} km")
            else:
                print("\n❌ No path found")
        
        # Example 2: Critical Substations (Hub Detection)
        print_section("2. Critical Infrastructure - Hub Detection")
        query = """
        MATCH (s:Substation)
        OPTIONAL MATCH (s)-[:TRANSMITS_TO]-(connected)
        WITH s, count(DISTINCT connected) as connection_count
        WHERE connection_count > 0
        RETURN s.id as id, s.name as name, s.type as type,
               s.voltage_kv as voltage_kv, connection_count
        ORDER BY connection_count DESC
        LIMIT 10
        """
        results = conn.execute_read(query)
        
        print("Top 10 Most Connected Substations (Network Hubs):")
        for i, sub in enumerate(results, 1):
            print(f"{i}. {sub['name']}")
            print(f"   Type: {sub['type']}, Voltage: {sub['voltage_kv']} kV")
            print(f"   Connections: {sub['connection_count']}")
        
        # Example 3: Power Plant Reach Analysis
        print_section("3. Power Plant Service Area Analysis")
        plants = infra_repo.get_all_power_plants()
        
        if plants:
            sample_plant = plants[0]
            print(f"Analyzing reach for: {sample_plant['name']}")
            
            # Count reachable customers
            query = """
            MATCH path = (p:PowerPlant {id: $plant_id})-[:GENERATES]->()
                         -[:TRANSMITS_TO*0..10]->()-[:SUPPLIES_POWER]->(c:Customer)
            WITH p, count(DISTINCT c) as customer_count,
                 avg(length(path)) as avg_path_length,
                 max(length(path)) as max_path_length
            RETURN customer_count, avg_path_length, max_path_length
            """
            results = conn.execute_read(query, {"plant_id": sample_plant['id']})
            
            if results:
                data = results[0]
                print(f"\nReachable Customers: {data['customer_count']}")
                print(f"Average Path Length: {data['avg_path_length']:.2f} hops")
                print(f"Maximum Path Length: {data['max_path_length']} hops")
        
        # Example 4: Network Redundancy Analysis
        print_section("4. Network Redundancy Analysis")
        query = """
        MATCH (c:Customer)
        OPTIONAL MATCH path = (p:PowerPlant)-[:GENERATES]->()
                              -[:TRANSMITS_TO*]->()-[:SUPPLIES_POWER]->(c)
        WITH c, count(DISTINCT p) as source_count
        RETURN c.id as customer_id, c.name as customer_name,
               c.type as customer_type, source_count,
               CASE 
                   WHEN source_count = 0 THEN 'ISOLATED'
                   WHEN source_count = 1 THEN 'SINGLE_SOURCE'
                   WHEN source_count = 2 THEN 'DUAL_SOURCE'
                   ELSE 'MULTI_SOURCE'
               END as redundancy_level
        ORDER BY source_count ASC, c.name
        """
        results = conn.execute_read(query)
        
        # Group by redundancy level
        by_level = {}
        for result in results:
            level = result['redundancy_level']
            if level not in by_level:
                by_level[level] = []
            by_level[level].append(result)
        
        print("Customers by Redundancy Level:\n")
        for level in ['ISOLATED', 'SINGLE_SOURCE', 'DUAL_SOURCE', 'MULTI_SOURCE']:
            if level in by_level:
                customers = by_level[level]
                print(f"{level}: {len(customers)} customer(s)")
                for customer in customers[:5]:  # Show first 5
                    print(f"  - {customer['customer_name']} ({customer['customer_type']}): "
                          f"{customer['source_count']} source(s)")
                if len(customers) > 5:
                    print(f"  ... and {len(customers) - 5} more")
                print()
        
        # Example 5: Transmission Bottleneck Detection
        print_section("5. Transmission Bottleneck Detection")
        query = """
        MATCH (s1:Substation)-[t:TRANSMITS_TO]->(s2:Substation)
        OPTIONAL MATCH path1 = ()-[:TRANSMITS_TO*]->(s1)
        OPTIONAL MATCH path2 = (s2)-[:TRANSMITS_TO*]->()
        WITH s1, s2, t,
             count(DISTINCT path1) as incoming_paths,
             count(DISTINCT path2) as outgoing_paths
        WHERE incoming_paths > 2 OR outgoing_paths > 2
        WITH s1, s2, t, incoming_paths, outgoing_paths,
             (incoming_paths + outgoing_paths) as total_traffic
        RETURN s1.name as from_substation, s2.name as to_substation,
               t.capacity_mw as capacity_mw, t.line_id as line_id,
               incoming_paths, outgoing_paths, total_traffic
        ORDER BY total_traffic DESC
        LIMIT 10
        """
        results = conn.execute_read(query)
        
        print("Potential Bottlenecks (High Traffic Transmission Lines):\n")
        for i, line in enumerate(results, 1):
            print(f"{i}. {line['line_id']}")
            print(f"   Route: {line['from_substation']} → {line['to_substation']}")
            print(f"   Capacity: {line['capacity_mw']} MW")
            print(f"   Traffic: {line['total_traffic']} paths "
                  f"({line['incoming_paths']} in, {line['outgoing_paths']} out)")
        
        # Example 6: Regional Connectivity Analysis
        print_section("6. Regional Connectivity Analysis")
        query = """
        MATCH (s:Substation)
        WITH s.region as region, count(s) as substations
        MATCH (sub:Substation {region: region})
        OPTIONAL MATCH (sub)-[:TRANSMITS_TO]-(connected)
        WITH region, substations, 
             count(DISTINCT connected) as total_connections,
             sum(sub.capacity_mva) as total_capacity
        RETURN region, substations, total_connections,
               total_capacity,
               CASE 
                   WHEN total_connections > substations * 2 THEN 'HIGHLY_CONNECTED'
                   WHEN total_connections > substations THEN 'WELL_CONNECTED'
                   ELSE 'SPARSE'
               END as connectivity_level
        ORDER BY total_connections DESC
        """
        results = conn.execute_read(query)
        
        print("Regional Network Connectivity:\n")
        for region in results:
            print(f"Region: {region['region']}")
            print(f"  Substations: {region['substations']}")
            print(f"  Connections: {region['total_connections']}")
            print(f"  Total Capacity: {region['total_capacity']:,.0f} MVA")
            print(f"  Connectivity: {region['connectivity_level']}")
            print()
        
        # Example 7: Alternative Path Analysis
        print_section("7. Alternative Path Analysis")
        
        if len(substations) >= 2:
            sub1 = substations[0]
            sub2 = substations[-1]
            
            print(f"Finding all paths (max 4 hops):")
            print(f"  From: {sub1['name']}")
            print(f"  To: {sub2['name']}")
            
            query = """
            MATCH path = (s1:Substation {id: $from_id})
                        -[:TRANSMITS_TO*1..4]-(s2:Substation {id: $to_id})
            WITH path, 
                 reduce(dist = 0, rel in relationships(path) | 
                        dist + rel.distance_km) as total_distance,
                 reduce(capacity = 999999, rel in relationships(path) | 
                        CASE WHEN rel.capacity_mw < capacity 
                        THEN rel.capacity_mw ELSE capacity END) as min_capacity
            RETURN [node in nodes(path) | node.name] as route,
                   length(path) as hops,
                   round(total_distance, 2) as distance_km,
                   min_capacity as bottleneck_capacity_mw
            ORDER BY hops, distance_km
            LIMIT 5
            """
            results = conn.execute_read(query, {
                "from_id": sub1['id'],
                "to_id": sub2['id']
            })
            
            if results:
                print(f"\nFound {len(results)} alternative path(s):\n")
                for i, path in enumerate(results, 1):
                    print(f"Path {i}: {path['hops']} hop(s), {path['distance_km']} km")
                    print(f"  Bottleneck Capacity: {path['bottleneck_capacity_mw']} MW")
                    print(f"  Route: {' → '.join(path['route'])}")
                    print()
            else:
                print("\n❌ No paths found within 4 hops")
        
    finally:
        conn.close()
        print("\n✅ Connection closed")


if __name__ == "__main__":
    main()
