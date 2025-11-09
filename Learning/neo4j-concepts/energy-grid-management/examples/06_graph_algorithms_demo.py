"""
Example 6: Graph Algorithms Demonstration
Shows Neo4j GDS graph algorithms in action.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.connection import Neo4jConnection
from src.algorithms.shortest_path import ShortestPathAlgorithms
from src.algorithms.centrality import CentralityAlgorithms
from src.algorithms.community_detection import CommunityDetectionAlgorithms
from src.algorithms.network_flow import NetworkFlowAlgorithms


def print_section(title: str):
    print(f"\n{'=' * 80}\n{title:^80}\n{'=' * 80}\n")


def main():
    conn = Neo4jConnection()
    driver = conn.get_driver()
    
    if not driver:
        print("Failed to connect to Neo4j")
        return
    
    try:
        # Get some substations for demo
        with driver.session() as session:
            result = session.run("MATCH (ss:Substation) RETURN ss.id as id, ss.name as name LIMIT 5")
            substations = [dict(r) for r in result]
        
        if len(substations) < 2:
            print("Need at least 2 substations in database")
            return
        
        # 1. Shortest Path Algorithms
        print_section("1. SHORTEST PATH ALGORITHMS")
        sp_algo = ShortestPathAlgorithms(driver)
        
        source = substations[0]
        target = substations[-1]
        
        print(f"Finding paths from {source['name']} to {target['name']}...\n")
        
        # All shortest paths
        paths = sp_algo.all_shortest_paths(source['id'], target['id'])
        print(f"Found {len(paths)} shortest path(s):")
        for i, path in enumerate(paths, 1):
            print(f"  Path {i}: {' -> '.join(path['node_names'])}")
            print(f"  Hops: {path['hop_count']}")
        
        # 2. Centrality Analysis
        print_section("2. CENTRALITY ANALYSIS")
        cent_algo = CentralityAlgorithms(driver)
        
        print("Most Connected Substations (Degree Centrality):")
        degree = cent_algo.degree_centrality(top_k=5)
        for i, node in enumerate(degree, 1):
            print(f"  {i}. {node['node_name']} - {node['degree']} connections")
        
        print("\nMost Important Hubs (PageRank):")
        pagerank = cent_algo.pagerank(top_k=5)
        for i, node in enumerate(pagerank, 1):
            print(f"  {i}. {node['node_name']} - Score: {node['pagerank_score']:.4f}")
        
        print("\nCritical Bridge Nodes:")
        critical = cent_algo.identify_critical_nodes(top_k=5)
        for i, node in enumerate(critical, 1):
            print(f"  {i}. {node['node_name']}")
            print(f"     Degree: {node['degree']}, Criticality: {node['criticality_score']:.4f}")
        
        # 3. Community Detection
        print_section("3. COMMUNITY DETECTION")
        comm_algo = CommunityDetectionAlgorithms(driver)
        
        print("Detecting communities with Louvain algorithm...\n")
        communities = comm_algo.louvain_communities()
        
        print(f"Found {len(communities)} communities:")
        for i, comm in enumerate(communities[:5], 1):
            print(f"\n  Community {i} ({comm['community_size']} members):")
            for member in comm['members'][:3]:
                print(f"    • {member['node_name']} ({member['location']})")
            if comm['community_size'] > 3:
                print(f"    ... and {comm['community_size'] - 3} more")
        
        # Triangle counting
        print("\n\nTriangle Count (Network Clustering):")
        triangles = comm_algo.triangle_count_clustering()
        for node in triangles[:5]:
            print(f"  {node['node_name']}: {node['triangleCount']} triangles, "
                  f"clustering: {node['clustering_coefficient']:.3f}")
        
        # 4. Network Flow Analysis
        print_section("4. NETWORK FLOW ANALYSIS")
        flow_algo = NetworkFlowAlgorithms(driver)
        
        print("Network Capacity Overview:")
        capacity = flow_algo.analyze_network_capacity()
        print(f"  Generation Capacity: {capacity['total_generation_capacity']:.0f} MW")
        print(f"  Total Load: {capacity['total_load']:.0f} MW")
        print(f"  Utilization: {capacity['generation_utilization']:.1%}")
        print(f"  Reserve Margin: {capacity['reserve_margin']:.1%}")
        
        print("\n\nBottleneck Analysis:")
        bottlenecks = flow_algo.identify_bottlenecks(threshold_utilization=0.7)
        if bottlenecks:
            for bottleneck in bottlenecks[:5]:
                print(f"  {bottleneck['line_name']}: {bottleneck['utilization']:.1%} utilization")
                print(f"    From: {bottleneck['from_substation']}")
                print(f"    To: {bottleneck['to_substation']}")
                print(f"    Risk: {bottleneck['risk_level']}")
        else:
            print("  ✅ No bottlenecks detected")
        
        print("\n\nLoad Distribution:")
        load_dist = flow_algo.calculate_load_distribution()
        for node in load_dist[:5]:
            print(f"  {node['substation_name']}: {node['utilization_pct']:.1f}% "
                  f"({node['load_level']})")
        
        # 5. Simulate Outage
        print_section("5. OUTAGE IMPACT SIMULATION")
        
        test_component = substations[1]
        print(f"Simulating outage of {test_component['name']}...\n")
        
        impact = flow_algo.simulate_outage_impact(test_component['id'], 'Substation')
        
        if impact:
            print(f"Impact Severity: {impact['impact_severity']}")
            print(f"Affected Customers: {impact['affected_customers']}")
            print(f"Affected Load: {impact['affected_load_mw']:.2f} MW")
            
            if 'reroute_analysis' in impact:
                reroute = impact['reroute_analysis']
                print(f"\nReroute Potential:")
                print(f"  Reroutable Customers: {reroute.get('reroutable_customers', 0)}")
                print(f"  Reroutable Load: {reroute.get('reroutable_load_mw', 0):.2f} MW")
        
        # 6. Network Diameter
        print_section("6. NETWORK TOPOLOGY METRICS")
        
        diameter = sp_algo.calculate_network_diameter()
        print(f"Network Diameter: {diameter['diameter']} hops")
        print(f"Average Path Length: {diameter['average_path_length']:.2f} hops")
        print(f"Minimum Path Length: {diameter['minimum_path_length']} hops")
        print(f"Total Paths Analyzed: {diameter['total_paths_analyzed']}")
        
        # 7. Power Flow Optimization
        print_section("7. POWER FLOW OPTIMIZATION")
        
        optimizations = flow_algo.optimize_power_flow()
        if optimizations:
            print(f"Found {len(optimizations)} underutilized power plants:\n")
            for plant in optimizations[:5]:
                print(f"  {plant['plant_name']} ({plant['plant_type']})")
                print(f"    Capacity: {plant['capacity']:.0f} MW")
                print(f"    Current Supply: {plant['current_supply']:.0f} MW")
                print(f"    Utilization: {plant['utilization_pct']:.1f}%")
                print(f"    Available: {plant['available_capacity']:.0f} MW")
        else:
            print("All plants operating at optimal utilization")
        
    finally:
        conn.close()


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("GRAPH ALGORITHMS DEMONSTRATION")
    print("=" * 80)
    main()
    print("\n" + "=" * 80)
    print("Complete!")
    print("=" * 80 + "\n")
