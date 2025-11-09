#!/usr/bin/env python3
"""
Setup Script 1: Create Schema

This script creates all indexes and constraints for the energy grid database.
Run this before loading data.
"""

import sys
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.connection import get_connection, close_connection

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def read_cypher_file(filename: str) -> str:
    """Read Cypher script from file."""
    cypher_dir = Path(__file__).parent.parent / "cypher"
    file_path = cypher_dir / filename
    
    if not file_path.exists():
        raise FileNotFoundError(f"Cypher file not found: {file_path}")
    
    with open(file_path, 'r') as f:
        return f.read()


def execute_cypher_statements(connection, script: str) -> None:
    """Execute multiple Cypher statements from a script."""
    # Split by semicolon and filter empty statements
    statements = [s.strip() for s in script.split(';') if s.strip() and not s.strip().startswith('//')]
    
    success_count = 0
    error_count = 0
    
    for stmt in statements:
        # Skip comments
        if stmt.startswith('//') or stmt.startswith('/*'):
            continue
        
        try:
            connection.execute_write(stmt)
            success_count += 1
            logger.info(f"✓ Executed statement successfully")
        except Exception as e:
            error_count += 1
            logger.warning(f"✗ Failed to execute statement: {e}")
            logger.debug(f"Statement: {stmt[:100]}...")
    
    logger.info(f"Execution complete: {success_count} successful, {error_count} failed")


def main():
    """Main execution function."""
    logger.info("=" * 60)
    logger.info("Creating Energy Grid Database Schema")
    logger.info("=" * 60)
    
    connection = None
    
    try:
        # Connect to database
        logger.info("\n1. Connecting to Neo4j...")
        connection = get_connection()
        
        if not connection.verify_connection():
            logger.error("Failed to connect to Neo4j")
            sys.exit(1)
        
        logger.info("✓ Connected successfully")
        
        # Read schema script
        logger.info("\n2. Reading schema creation script...")
        schema_script = read_cypher_file("01_schema_creation.cypher")
        logger.info("✓ Schema script loaded")
        
        # Execute schema creation
        logger.info("\n3. Creating constraints and indexes...")
        execute_cypher_statements(connection, schema_script)
        logger.info("✓ Schema created")
        
        # Verify schema
        logger.info("\n4. Verifying schema...")
        
        # Check constraints
        constraints = connection.execute_read("SHOW CONSTRAINTS")
        logger.info(f"✓ Created {len(constraints)} constraints")
        
        # Check indexes
        indexes = connection.execute_read("SHOW INDEXES")
        logger.info(f"✓ Created {len(indexes)} indexes")
        
        logger.info("\n" + "=" * 60)
        logger.info("Schema creation completed successfully!")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"\n✗ Error during schema creation: {e}")
        sys.exit(1)
    
    finally:
        if connection:
            close_connection()


if __name__ == "__main__":
    main()
