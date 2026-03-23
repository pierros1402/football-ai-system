from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    DATABASE_URL: str
    SENDGRID_API_KEY: str
    EMAIL_FROM: str
    SECRET_KEY: str = "supersecretkey"
    ALGORITHM: str = "HS256"   # <── ΠΡΟΣΘΕΣΕ ΑΥΤΟ

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
