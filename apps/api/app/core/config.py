from typing import Literal

from pydantic import Field, model_validator
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
    postgresql_connect_timeout_seconds: int = Field(default=5, ge=1, le=30)
    postgresql_pool_timeout_seconds: int = Field(default=5, ge=1, le=30)
    minio_connect_timeout_seconds: float = Field(default=3.0, gt=0, le=30)
    minio_read_timeout_seconds: float = Field(default=10.0, gt=0, le=120)
    document_max_file_size: int = 104_857_600
    rag_chunk_size: int = Field(default=1_000, ge=100, le=10_000)
    rag_chunk_overlap: int = Field(default=150, ge=0, le=2_000)
    rag_ai_provider: str = "openai"
    rag_embedding_model: str = "text-embedding-3-small"
    rag_chat_model: str = "gpt-4o-mini"
    rag_embedding_dimensions: int = Field(default=1_536, ge=1, le=4_096)
    rag_search_limit: int = Field(default=5, ge=1, le=20)
    openai_api_key: str = ""
    ai_connect_timeout_seconds: float = Field(default=5.0, gt=0, le=30)
    ai_total_timeout_seconds: float = Field(default=30.0, gt=0, le=300)
    ai_max_attempts: int = Field(default=3, ge=1, le=10)
    ai_retry_base_seconds: float = Field(default=0.25, ge=0, le=30)
    ai_retry_max_seconds: float = Field(default=2.0, ge=0, le=60)
    ai_retry_jitter_ratio: float = Field(default=0.2, ge=0, le=1)
    ai_concurrency_limit: int = Field(default=8, ge=1, le=1_000)
    ai_queue_timeout_seconds: float = Field(default=0.1, ge=0, le=30)
    deterministic_ai_delay_seconds: float = Field(default=0.05, ge=0, le=5)
    cors_origins: list[str] = ["http://localhost:3000"]
    auth_secret_key: str = ""
    auth_token_expiration_minutes: int = 30
    auth_cookie_name: str = "vena_ia_session"
    auth_cookie_secure: bool = False
    password_hash_iterations: int = 600_000
    auth_login_rate_limit_requests: int = Field(default=10, ge=1, le=10_000)
    auth_registration_rate_limit_requests: int = Field(default=5, ge=1, le=10_000)
    auth_rate_limit_window_seconds: int = Field(default=60, ge=1, le=86_400)
    auth_security_store: Literal["redis", "memory"] = "redis"
    auth_redis_prefix: str = Field(
        default="vena_ia:auth",
        min_length=1,
        max_length=128,
        pattern=r"^[A-Za-z0-9][A-Za-z0-9:_-]*$",
    )
    auth_redis_timeout_seconds: float = Field(default=1.0, gt=0, le=30)
    jobs_queue_provider: Literal["redis", "memory"] = "redis"
    jobs_redis_prefix: str = Field(
        default="vena_ia:jobs",
        min_length=1,
        max_length=128,
        pattern=r"^[A-Za-z0-9][A-Za-z0-9:_-]*$",
    )
    jobs_redis_timeout_seconds: float = Field(default=1.0, gt=0, le=30)
    jobs_lease_seconds: int = Field(default=60, ge=5, le=3600)
    jobs_timeout_seconds: int = Field(default=900, ge=1, le=86_400)
    jobs_max_attempts: int = Field(default=3, ge=1, le=20)
    jobs_retry_base_seconds: float = Field(default=2.0, ge=0.1, le=3600)
    jobs_retry_max_seconds: float = Field(default=300.0, ge=0.1, le=3600)
    jobs_retry_jitter_ratio: float = Field(default=0.2, ge=0, le=1)
    security_audit_retention_days: int = Field(default=90, ge=1, le=3_650)
    observability_collection_enabled: bool = True
    observability_metrics_endpoint_enabled: bool = False
    observability_alert_cooldown_seconds: float = Field(default=30, ge=0, le=86_400)
    observability_repeated_auth_failure_threshold: int = Field(default=5, ge=1, le=1_000)
    observability_rate_limit_threshold: int = Field(default=1, ge=1, le=1_000)
    observability_processing_failure_threshold: int = Field(default=3, ge=1, le=1_000)
    observability_readiness_degradation_threshold: int = Field(default=1, ge=1, le=100)
    observability_dependency_failure_threshold: int = Field(default=1, ge=1, le=100)
    observability_internal_error_threshold: int = Field(default=1, ge=1, le=100)

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    @model_validator(mode="after")
    def reject_production_memory_security_store(self) -> "Settings":
        if self.ai_retry_max_seconds < self.ai_retry_base_seconds:
            raise ValueError("AI retry maximum must be at least the base delay")
        if self.ai_connect_timeout_seconds > self.ai_total_timeout_seconds:
            raise ValueError("AI connect timeout cannot exceed the total timeout")
        if self.jobs_retry_max_seconds < self.jobs_retry_base_seconds:
            raise ValueError("Job retry maximum must be at least the base delay")
        if (
            self.app_env.lower() in {"production", "prod"}
            and self.auth_security_store == "memory"
        ):
            raise ValueError("AUTH_SECURITY_STORE=memory is forbidden in production")
        if (
            self.app_env.lower() in {"production", "prod"}
            and self.jobs_queue_provider == "memory"
        ):
            raise ValueError("JOBS_QUEUE_PROVIDER=memory is forbidden in production")
        return self


settings = Settings()
