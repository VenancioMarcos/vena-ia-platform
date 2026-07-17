from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    database_url: str = "postgresql+psycopg://vena_ia:change_me@localhost:5432/vena_ia"
    sqlalchemy_database_url: str = "postgresql+psycopg://vena_ia:change_me@localhost:5432/vena_ia"
    redis_url: str = "redis://localhost:6379/0"
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "change_me"
    minio_secret_key: str = "change_me"
    minio_bucket: str = "vena-ia-files"
    minio_secure: bool = False
    document_max_file_size: int = 104_857_600
    openai_api_key: str = ""
    cors_origins: list[str] = ["http://localhost:3000"]

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()
