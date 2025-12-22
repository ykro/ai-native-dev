from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyHttpUrl, Field

class Settings(BaseSettings):
    """
    Application settings and environment validation using Pydantic.
    """
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Required variables
    FRONTEND_URL: AnyHttpUrl = Field(..., description="URL of the frontend application for CORS")
    PORT: int = Field(default=8000, description="Port to run the server on")
    ENVIRONMENT: str = Field(default="development", description="App environment (development/production)")

settings = Settings()
