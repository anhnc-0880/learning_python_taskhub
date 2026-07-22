from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "TaskHub API"
    environment: str = "local"
    database_url: str = "sqlite:///./taskhub.db"
    secret_key: str = Field(..., min_length=16)
    access_token_expire_seconds: int = 60 * 60
    refresh_token_expire_days: int = 7
    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
