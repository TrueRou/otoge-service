from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="USAGI_MAIMAI_PROBER_", case_sensitive=False)

    bind_host: str = "127.0.0.1"
    bind_port: int = 7100
    database_url: str = f"sqlite+aiosqlite:///database.db"

    lxns_developer_token: str | None = None
    divingfish_developer_token: str | None = None
    arcade_proxy: str | None = None


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
