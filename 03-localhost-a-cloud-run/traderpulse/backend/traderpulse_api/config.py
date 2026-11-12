from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Ajustes(BaseSettings):
    """Configuración que llega por variables de entorno (Cloud Run las inyecta)."""

    # Token compartido entre el servidor de Next.js y este BFF.
    # En Cloud Run viene de Secret Manager; vacío desactiva la verificación (solo local).
    traderpulse_token: str = ""
    # "ejemplo" responde sin llamar a ningún modelo; "vertex" usa Gemini en Vertex AI.
    sentimiento_fuente: str = "ejemplo"
    google_cloud_project: str = ""
    google_cloud_location: str = "global"
    modelo_gemini: str = "gemini-3.8-flash"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def ajustes() -> Ajustes:
    return Ajustes()
