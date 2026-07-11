from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    database_url: str = "postgresql+psycopg://vena_ia:change_me@localhost:5432/vena_ia"
    sqlalchemy_database_url: str = "postgresql+psycopg://vena_ia:change_me@localhost:5432/vena_ia"
    redis_url: str = "redis://localhost:6379/0"
    openai_api_key: str = ""
    cors_origins: list[str] = ["http://localhost:3000"]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()

