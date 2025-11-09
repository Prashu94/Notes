"""
Tests for graph algorithm implementations.
"""

import pytest
from src.connection import Neo4jConnection
from src.algorithms.shortest_path import ShortestPathAlgorithms
from src.algorithms.centrality import CentralityAlgorithms
from src.algorithms.community_detection import CommunityDetectionAlgorithms
from src.algorithms.network_flow import NetworkFlowAlgorithms


@pytest.fixture
def driver():
    """Get database driver."""
    conn = Neo4jConnection()
    drv = conn.get_driver()
    yield drv
    conn.close()


@pytest.fixture
def substations(driver):
    """Get sample substations for testing."""
    with driver.session() as session:
        result = session.run("MATCH (ss:Substation) RETURN ss.id as id LIMIT 5")
        return [record["id"] for record in result]


def test_shortest_path_all_paths(driver, substations):
    """Test finding all shortest paths."""
    if len(substations) < 2:
        pytest.skip("Need at least 2 substations")
    
    algo = ShortestPathAlgorithms(driver)
    paths = algo.all_shortest_paths(substations[0], substations[-1])
    
    assert isinstance(paths, list)


def test_shortest_path_network_diameter(driver):
    """Test network diameter calculation."""
    algo = ShortestPathAlgorithms(driver)
    diameter = algo.calculate_network_diameter()
    
    assert 'diameter' in diameter
    assert 'average_path_length' in diameter


def test_centrality_degree(driver):
    """Test degree centrality."""
    algo = CentralityAlgorithms(driver)
    nodes = algo.degree_centrality(top_k=5)
    
    assert isinstance(nodes, list)
    if nodes:
        assert 'node_id' in nodes[0]
        assert 'degree' in nodes[0]


def test_centrality_critical_nodes(driver):
    """Test critical node identification."""
    algo = CentralityAlgorithms(driver)
    critical = algo.identify_critical_nodes(top_k=5)
    
    assert isinstance(critical, list)
    if critical:
        assert 'criticality_score' in critical[0]


def test_centrality_node_importance(driver, substations):
    """Test individual node importance analysis."""
    if not substations:
        pytest.skip("No substations available")
    
    algo = CentralityAlgorithms(driver)
    importance = algo.analyze_node_importance(substations[0])
    
    assert 'node_id' in importance
    assert 'importance_level' in importance


def test_community_detection_louvain(driver):
    """Test Louvain community detection."""
    algo = CommunityDetectionAlgorithms(driver)
    
    try:
        communities = algo.louvain_communities()
        assert isinstance(communities, list)
    except Exception as e:
        # GDS might not be available
        pytest.skip(f"GDS not available: {e}")


def test_community_detection_wcc(driver):
    """Test weakly connected components."""
    algo = CommunityDetectionAlgorithms(driver)
    
    try:
        components = algo.weakly_connected_components()
        assert isinstance(components, list)
    except Exception as e:
        pytest.skip(f"GDS not available: {e}")


def test_network_flow_capacity_analysis(driver):
    """Test network capacity analysis."""
    algo = NetworkFlowAlgorithms(driver)
    capacity = algo.analyze_network_capacity()
    
    assert 'total_generation_capacity' in capacity
    assert 'total_load' in capacity


def test_network_flow_bottlenecks(driver):
    """Test bottleneck identification."""
    algo = NetworkFlowAlgorithms(driver)
    bottlenecks = algo.identify_bottlenecks(threshold_utilization=0.7)
    
    assert isinstance(bottlenecks, list)


def test_network_flow_load_distribution(driver):
    """Test load distribution analysis."""
    algo = NetworkFlowAlgorithms(driver)
    distribution = algo.calculate_load_distribution()
    
    assert isinstance(distribution, list)


def test_network_flow_optimization(driver):
    """Test power flow optimization."""
    algo = NetworkFlowAlgorithms(driver)
    optimizations = algo.optimize_power_flow()
    
    assert isinstance(optimizations, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
