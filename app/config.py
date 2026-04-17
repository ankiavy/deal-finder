from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "Deal Finder API"
    debug: bool = True
    base_url: str = "http://localhost:8000"

    # Database
    database_url: str = (
        "postgresql+asyncpg://dealuser:dealpass@localhost:5432/dealfinder"
    )

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Amazon PAAPI 5.0
    amazon_access_key: str = ""
    amazon_secret_key: str = ""
    amazon_partner_tag: str = "yoursite-21"
    amazon_region: str = "in"

    # Flipkart Affiliate
    flipkart_api_token: str = ""

    # Cache TTL
    search_cache_ttl: int = 300   # 5 minutes
    deals_cache_ttl: int = 600    # 10 minutes

    # Dev mode: serve mock data instead of real APIs
    use_mock_data: bool = True


settings = Settings()
