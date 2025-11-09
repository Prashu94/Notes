"""
Repositories Package Initialization

Exports all repository classes for data access.
"""

from .infrastructure_repo import InfrastructureRepository

__all__ = [
    "InfrastructureRepository",
]
