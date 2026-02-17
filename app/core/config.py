from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./app.db"
    PROCESS_DELAY_SECONDS: int = 30
    PROCESS_INTERVAL_SECONDS: int = 15
    LOG_SQL: bool = False
    API_V1_STR: str = "/v1"

    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)


@lru_cache
def get_settings() -> Settings:
    return Settings()
