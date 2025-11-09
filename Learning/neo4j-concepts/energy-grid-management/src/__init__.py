"""
Energy Grid Management System - Python Package Initialization
"""

__version__ = "1.0.0"
__author__ = "Energy Grid Team"

from .config import get_settings, Settings
from .connection import get_connection, close_connection, Neo4jConnection

__all__ = [
    "get_settings",
    "Settings",
    "get_connection",
    "close_connection",
    "Neo4jConnection",
]
