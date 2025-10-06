"""Application configuration using Pydantic Settings."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # API Settings
    api_title: str = "JobBooster API"
    api_version: str = "1.0.0"
    api_prefix: str = "/api/v1"
    debug: bool = False

    # OpenAI
    openai_api_key: str = Field(..., alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o-mini", alias="OPENAI_MODEL")

    # Google Gemini
    google_api_key: str = Field(..., alias="GOOGLE_API_KEY")
    gemini_model: str = Field(default="gemini-1.5-pro", alias="GEMINI_MODEL")

    # Anthropic Claude
    anthropic_api_key: str | None = Field(default=None, alias="ANTHROPIC_API_KEY")

    # Hugging Face
    huggingface_api_key: str = Field(..., alias="HUGGINGFACE_API_KEY")

    # Qdrant
    qdrant_url: str = Field(default="http://localhost:6333", alias="QDRANT_URL")
    qdrant_api_key: str | None = Field(default=None, alias="QDRANT_API_KEY")
    qdrant_collection: str = Field(default="user_info", alias="QDRANT_COLLECTION")
    qdrant_cluster: str = Field(default="jobbooster", alias="QDRANT_CLUSTER")

    # Embeddings
    embedding_model: str = Field(
        default="intfloat/multilingual-e5-base",
        alias="EMBEDDING_MODEL",
    )
    reranker_model: str = Field(
        default="BAAI/bge-reranker-base",
        alias="RERANKER_MODEL",
    )

    # Langfuse
    langfuse_public_key: str = Field(..., alias="LANGFUSE_PUBLIC_KEY")
    langfuse_secret_key: str = Field(..., alias="LANGFUSE_SECRET_KEY")
    langfuse_host: str = Field(
        default="https://cloud.langfuse.com",
        alias="LANGFUSE_HOST",
    )

    # Chunking
    chunk_size: int = Field(default=400, alias="CHUNK_SIZE")
    chunk_overlap: int = Field(default=50, alias="CHUNK_OVERLAP")

    # Paths
    data_dir: str = Field(default="data", alias="DATA_DIR")


settings = Settings()
