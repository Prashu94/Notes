"""
Tests for Neo4j connection functionality.
"""

import pytest
from src.connection import Neo4jConnection
from src.config import Settings


def test_connection_singleton():
    """Test that connection follows singleton pattern."""
    conn1 = Neo4jConnection()
    conn2 = Neo4jConnection()
    assert conn1 is conn2


def test_driver_initialization():
    """Test driver initialization."""
    conn = Neo4jConnection()
    driver = conn.get_driver()
    assert driver is not None


def test_database_connectivity():
    """Test actual database connection."""
    conn = Neo4jConnection()
    with conn.get_session() as session:
        result = session.run("RETURN 1 as test")
        record = result.single()
        assert record["test"] == 1


def test_transaction_execution():
    """Test transaction execution."""
    conn = Neo4jConnection()
    
    def test_query(tx):
        result = tx.run("RETURN 2 + 2 as sum")
        return result.single()["sum"]
    
    with conn.get_session() as session:
        result = session.execute_read(test_query)
        assert result == 4


def test_connection_close():
    """Test connection cleanup."""
    conn = Neo4jConnection()
    driver = conn.get_driver()
    assert driver is not None
    
    conn.close()
    # After close, getting driver should reinitialize
    driver2 = conn.get_driver()
    assert driver2 is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
