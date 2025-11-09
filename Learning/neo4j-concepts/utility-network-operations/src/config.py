"""
Utility Network Operations - Configuration Module

Manages all configuration settings including Neo4j connection,
utility type (water/gas), and operational thresholds.
"""

import os
from typing import Optional, Literal
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
    neo4j_uri: str = Field(default="bolt://localhost:7688", alias="NEO4J_URI")
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
    utility_type: Literal["water", "gas"] = Field(default="water", alias="UTILITY_TYPE")
    
    # Vector Search Configuration
    vector_dimension: int = Field(default=1536, alias="VECTOR_DIMENSION")
    vector_similarity_function: str = Field(
        default="cosine", 
        alias="VECTOR_SIMILARITY_FUNCTION"
    )
    
    # Data Generation
    generate_synthetic_data: bool = Field(default=True, alias="GENERATE_SYNTHETIC_DATA")
    num_pipeline_segments: int = Field(default=500, alias="NUM_PIPELINE_SEGMENTS")
    num_pumping_stations: int = Field(default=20, alias="NUM_PUMPING_STATIONS")
    num_storage_tanks: int = Field(default=10, alias="NUM_STORAGE_TANKS")
    num_meters: int = Field(default=50000, alias="NUM_METERS")
    num_customers: int = Field(default=50000, alias="NUM_CUSTOMERS")
    
    # Leak Detection Thresholds
    pressure_threshold_min: float = Field(default=2.0, alias="PRESSURE_THRESHOLD_MIN")
    pressure_threshold_max: float = Field(default=8.0, alias="PRESSURE_THRESHOLD_MAX")
    flow_anomaly_threshold: float = Field(default=2.5, alias="FLOW_ANOMALY_THRESHOLD")
    
    # Billing Configuration
    billing_cycle_day: int = Field(default=1, alias="BILLING_CYCLE_DAY")
    water_rate_per_m3: float = Field(default=2.50, alias="WATER_RATE_PER_M3")
    gas_rate_per_m3: float = Field(default=0.75, alias="GAS_RATE_PER_M3")
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment.lower() == "development"
    
    @property
    def is_water_utility(self) -> bool:
        """Check if utility type is water."""
        return self.utility_type == "water"
    
    @property
    def is_gas_utility(self) -> bool:
        """Check if utility type is gas."""
        return self.utility_type == "gas"
    
    @property
    def consumption_rate(self) -> float:
        """Get consumption rate based on utility type."""
        return self.water_rate_per_m3 if self.is_water_utility else self.gas_rate_per_m3
    
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
