"""
Configuration settings for the Logistics AI Control System.
"""
import os
from pathlib import Path
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Project paths
    PROJECT_ROOT: Path = Path(__file__).parent.parent
    DATA_DIR: Path = PROJECT_ROOT / "data"
    CONFIG_DIR: Path = PROJECT_ROOT / "config"

    # Grok/xAI API Configuration
    XAI_API_KEY: str = Field(default="", description="xAI API key for Grok")
    XAI_BASE_URL: str = Field(
        default="https://api.x.ai/v1",
        description="xAI API base URL"
    )
    GROK_MODEL: str = Field(
        default="grok-beta",
        description="Grok model to use"
    )

    # LLM Settings
    LLM_TEMPERATURE: float = Field(default=0.7, ge=0.0, le=2.0)
    LLM_MAX_TOKENS: int = Field(default=4096, ge=1)
    LLM_TIMEOUT: int = Field(default=60, description="API timeout in seconds")
    LLM_MAX_RETRIES: int = Field(default=3, ge=1)

    # Control Loop Settings
    OBSERVATION_INTERVAL: int = Field(
        default=30,
        description="Seconds between observation cycles"
    )
    MAX_PLANNING_SCENARIOS: int = Field(
        default=5,
        description="Maximum scenarios to generate per planning cycle"
    )
    DECISION_CONFIDENCE_THRESHOLD: float = Field(
        default=0.7,
        description="Minimum confidence for automated decisions"
    )

    # Simulation Settings
    DEFAULT_TRUCK_SPEED_KMH: float = Field(default=60.0)
    TRAFFIC_DELAY_MULTIPLIER: float = Field(default=1.5)
    FUEL_CONSUMPTION_RATE: float = Field(
        default=0.3,
        description="Liters per km"
    )

    # API Settings
    API_HOST: str = Field(default="0.0.0.0")
    API_PORT: int = Field(default=8000)
    CORS_ORIGINS: list[str] = Field(default=["http://localhost:3000"])

    # Logging
    LOG_LEVEL: str = Field(default="INFO")
    LOG_FORMAT: str = Field(default="json")

    # Production Mode
    HEADLESS_MODE: bool = Field(
        default=False,
        description="Run without interactive prompts"
    )
    CONTINUOUS_LOOP: bool = Field(
        default=False,
        description="Run control loop continuously"
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get the global settings instance."""
    return settings
