from pydantic import Field
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
    rag_chunk_size: int = Field(default=1_000, ge=100, le=10_000)
    rag_chunk_overlap: int = Field(default=150, ge=0, le=2_000)
    openai_api_key: str = ""
    cors_origins: list[str] = ["http://localhost:3000"]
    auth_secret_key: str = ""
    auth_token_expiration_minutes: int = 30
    auth_cookie_name: str = "vena_ia_session"
    auth_cookie_secure: bool = False
    password_hash_iterations: int = 600_000

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()
