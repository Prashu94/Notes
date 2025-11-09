"""
Utility Network Operations - Neo4j Connection Module

This module provides connection management for Neo4j database.
Identical to energy grid connection module but configured for utility networks.
"""

import logging
from contextlib import contextmanager
from typing import Optional, Dict, Any, List
from neo4j import GraphDatabase, Driver, Session, Transaction
from neo4j.exceptions import ServiceUnavailable, SessionExpired

from .config import get_settings

logger = logging.getLogger(__name__)


class Neo4jConnection:
    """Manages Neo4j database connections with pooling and error handling."""
    
    def __init__(self, uri: Optional[str] = None, user: Optional[str] = None, 
                 password: Optional[str] = None, database: Optional[str] = None):
        """
        Initialize Neo4j connection.
        
        Args:
            uri: Neo4j connection URI (default from config)
            user: Database username (default from config)
            password: Database password (default from config)
            database: Database name (default from config)
        """
        settings = get_settings()
        
        self.uri = uri or settings.neo4j_uri
        self.user = user or settings.neo4j_user
        self.password = password or settings.neo4j_password
        self.database = database or settings.neo4j_database
        
        self._driver: Optional[Driver] = None
        
    def connect(self) -> None:
        """Establish connection to Neo4j database."""
        try:
            self._driver = GraphDatabase.driver(
                self.uri,
                auth=(self.user, self.password),
                max_connection_lifetime=3600,
                max_connection_pool_size=50,
                connection_acquisition_timeout=60
            )
            self._driver.verify_connectivity()
            logger.info(f"Successfully connected to Neo4j at {self.uri}")
        except ServiceUnavailable as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            raise
    
    def close(self) -> None:
        """Close the Neo4j driver and all connections."""
        if self._driver:
            self._driver.close()
            logger.info("Neo4j connection closed")
    
    @property
    def driver(self) -> Driver:
        """Get the Neo4j driver instance."""
        if not self._driver:
            self.connect()
        return self._driver
    
    @contextmanager
    def get_session(self, **kwargs) -> Session:
        """Context manager for Neo4j session."""
        session = self.driver.session(database=self.database, **kwargs)
        try:
            yield session
        except SessionExpired:
            logger.warning("Session expired, creating new session")
            session = self.driver.session(database=self.database, **kwargs)
            yield session
        finally:
            session.close()
    
    def execute_query(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Execute a Cypher query and return results."""
        with self.get_session() as session:
            result = session.run(query, parameters or {})
            return [record.data() for record in result]
    
    def execute_write(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Execute a write transaction."""
        def _execute(tx: Transaction) -> List[Dict[str, Any]]:
            result = tx.run(query, parameters or {})
            return [record.data() for record in result]
        
        with self.get_session() as session:
            return session.execute_write(_execute)
    
    def execute_read(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Execute a read transaction."""
        def _execute(tx: Transaction) -> List[Dict[str, Any]]:
            result = tx.run(query, parameters or {})
            return [record.data() for record in result]
        
        with self.get_session() as session:
            return session.execute_read(_execute)
    
    def verify_connection(self) -> bool:
        """Verify that the connection is working."""
        try:
            result = self.execute_read("RETURN 1 as test")
            return len(result) > 0 and result[0].get("test") == 1
        except Exception as e:
            logger.error(f"Connection verification failed: {e}")
            return False
    
    def get_node_count(self) -> int:
        """Get total number of nodes in the database."""
        query = "MATCH (n) RETURN count(n) as count"
        result = self.execute_read(query)
        return result[0]["count"] if result else 0
    
    def get_relationship_count(self) -> int:
        """Get total number of relationships in the database."""
        query = "MATCH ()-[r]->() RETURN count(r) as count"
        result = self.execute_read(query)
        return result[0]["count"] if result else 0


# Global connection instance
_connection: Optional[Neo4jConnection] = None


def get_connection() -> Neo4jConnection:
    """Get the global Neo4j connection instance."""
    global _connection
    if _connection is None:
        _connection = Neo4jConnection()
        _connection.connect()
    return _connection


def close_connection() -> None:
    """Close the global Neo4j connection."""
    global _connection
    if _connection:
        _connection.close()
        _connection = None
