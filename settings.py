from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    REDIS_URL: str = "redis://redis:6379/0"
    TIME_FOR_UPDATE_ORDER: int = 5
    API_KEY: str = "api_key"
    API_SECRET: str = "api_secret"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
