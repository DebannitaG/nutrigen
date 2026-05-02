from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    groq_api_key: str = ""
    mongodb_url: str = "mongodb://localhost:27017"
    database_name: str = "nutrigen"
    redis_url: str = "redis://localhost:6379"
    secret_key: str = "nutrigen-secret-2024"
    environment: str = "production"

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()