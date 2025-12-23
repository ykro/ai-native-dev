from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    APP_NAME: str = "TraderPulse API"
    VERSION: str = "1.0.0"
    
    # External APIs
    ALPHA_VANTAGE_KEY: str
    GEMINI_API_KEY: str
    
    # CORS (comma separated list of origins)
    CORS_ORIGINS: str = "http://localhost:3000"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

@lru_cache
def get_settings():
    return Settings()
