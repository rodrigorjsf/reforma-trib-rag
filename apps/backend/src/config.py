from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # API Keys
    groq_api_key: str = ""
    auth0_domain: str = ""
    auth0_client_id: str = ""
    auth0_client_secret: str = ""

    # Redis
    redis_url: str = "redis://localhost:6379"

    # ChromaDB
    chroma_persist_directory: str = "./chroma_data"

    # Rate Limits
    free_tier_daily_limit: int = 10
    free_tier_rpm: int = 5
    paid_tier_rpm: int = 30

    # LLM Settings
    llm_model: str = "mixtral-8x7b-32768"
    llm_max_tokens: int = 800
    generator_temperature: float = 0.1
    validator_temperature: float = 0.0

    # App Settings
    debug: bool = False
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    # Scraping Worker Configuration
    scraping_worker_enabled: bool = True
    scraping_worker_poll_interval: int = 5
    scraping_worker_max_retries: int = 3

    # Queue Configuration
    queue_backend: str = "sqlite"
    queue_db_path: str = "./data/scraping_queue.db"

    # Firecrawl Configuration
    firecrawl_timeout: int = 60
    firecrawl_max_retries: int = 3

    # Storage Configuration
    docs_path: str = "./docs"
    min_disk_space_gb: int = 1

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
