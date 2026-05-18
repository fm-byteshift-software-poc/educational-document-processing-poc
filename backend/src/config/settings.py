from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[2]

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

    DATABASE_URL: str = str(BACKEND_ROOT / "poc.db")
    STORAGE_PATH: str = str(BACKEND_ROOT / "storage")
    
    SECRET_KEY: str = "dev-secret-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_HOURS: int = 24
    HF_API_TOKEN: str = ""
    APP_ENV: str = "development"

settings = Settings()