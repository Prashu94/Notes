"""
Energy Grid Management System - Configuration Module

This module handles all configuration settings for the application,
including Neo4j connection parameters and environment variables.
"""

import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Neo4j Configuration
    neo4j_uri: str = Field(default="bolt://localhost:7687", alias="NEO4J_URI")
    neo4j_user: str = Field(default="neo4j", alias="NEO4J_USER")
    neo4j_password: str = Field(default="password", alias="NEO4J_PASSWORD")
    neo4j_database: str = Field(default="neo4j", alias="NEO4J_DATABASE")
    
    # OpenAI Configuration
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4", alias="OPENAI_MODEL")
    openai_embedding_model: str = Field(
        default="text-embedding-3-small", 
        alias="OPENAI_EMBEDDING_MODEL"
    )
    
    # Application Configuration
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    environment: str = Field(default="development", alias="ENVIRONMENT")
    
    # Vector Search Configuration
    vector_dimension: int = Field(default=1536, alias="VECTOR_DIMENSION")
    vector_similarity_function: str = Field(
        default="cosine", 
        alias="VECTOR_SIMILARITY_FUNCTION"
    )
    
    # Data Generation
    generate_synthetic_data: bool = Field(default=True, alias="GENERATE_SYNTHETIC_DATA")
    num_power_plants: int = Field(default=20, alias="NUM_POWER_PLANTS")
    num_substations: int = Field(default=100, alias="NUM_SUBSTATIONS")
    num_transmission_lines: int = Field(default=200, alias="NUM_TRANSMISSION_LINES")
    num_customers: int = Field(default=10000, alias="NUM_CUSTOMERS")
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment.lower() == "development"
    
    def get_neo4j_config(self) -> dict:
        """Get Neo4j connection configuration as dictionary."""
        return {
            "uri": self.neo4j_uri,
            "auth": (self.neo4j_user, self.neo4j_password),
            "database": self.neo4j_database
        }


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get the global settings instance."""
    return settings
