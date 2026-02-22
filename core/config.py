from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Which env file to load: ".local.env" or ".prod.env"
    ENV_FILE: str = ".local.env"

    # Database
    DATABASE_URL: str

    # JWT
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRY_DAYS: int = 90

    # HUD (optional)
    HUD_API_TOKEN: str | None = None
    
    API_NINJAS_KEY: str | None = None

    model_config = SettingsConfigDict(
        env_file=".local.env",   # default; we override below
        env_file_encoding="utf-8",
        extra="ignore",
    )


# Load settings from ENV_FILE if it exists in env vars.
# Example:
#   export ENV_FILE=.prod.env
#   uvicorn app.main:app ...
import os

_env_file = os.getenv("ENV_FILE", ".local.env")
settings = Settings(_env_file=_env_file)