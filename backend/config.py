from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    anthropic_api_key: str
    tavily_api_key: str = ""
    database_url: str = "sqlite+aiosqlite:///./crm.db"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings():
    return Settings()
