from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    bot_token: str
    group_id: int
    database_url: str

    max_files: int = 3
    max_subject_len: int = 150
    max_body_len: int = 3000
    retry_interval_sec: int = 60


@lru_cache
def get_settings() -> Settings:
    return Settings()
