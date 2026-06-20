from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = "development"
    auth_disabled: bool = False
    port: int = 8000
    log_level: str = "info"
    cors_origins: str = "http://localhost:5173"

    # Gemini
    google_api_key: str
    gemini_model: str = "gemini-2.5-flash"
    embedding_model: str = "models/gemini-embedding-001"
    embedding_dimensions: int = 3072

    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str | None = None
    qdrant_collection_name: str = "codigo_nacional_transito"

    database_url: str = "postgresql://postgres:postgres@localhost:5432/vialbot"

    cognito_region: str = "us-east-1"
    cognito_user_pool_id: str
    cognito_app_client_id: str

    admin_api_key: str | None = None

    langchain_tracing_v2: bool = False
    langchain_api_key: str | None = None
    langchain_project: str = "vialbot"

    @property
    def cognito_jwks_url(self) -> str:
        return (
            f"https://cognito-idp.{self.cognito_region}.amazonaws.com/"
            f"{self.cognito_user_pool_id}/.well-known/jwks.json"
        )

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
