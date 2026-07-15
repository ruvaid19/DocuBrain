from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "DocuBrain Enterprise RAG API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str
    
    # Qdrant
    QDRANT_HOST: Optional[str] = None
    QDRANT_PORT: Optional[int] = None
    QDRANT_URL: Optional[str] = None
    QDRANT_API_KEY: Optional[str] = None
    
    # Gemini (Google)
    GEMINI_API_KEY: str

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

settings = Settings()
