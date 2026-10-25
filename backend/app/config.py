from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    database_url: str = Field(min_length=1)
    test_database_url: str | None = None
    jwt_secret: str = Field(min_length=1)

    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = Field(default=60, gt=0)
    environment: str = "development"
    cors_origins: list[str] = ["http://localhost:8501"]

    @field_validator("database_url", "jwt_secret")
    @classmethod
    def reject_empty_values(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("This setting must not be empty")
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
