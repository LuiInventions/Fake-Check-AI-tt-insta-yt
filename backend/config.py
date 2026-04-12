from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o"
    WHISPER_MODEL: str = "whisper-1"
    APP_NAME: str = "FakeCheck"
    APP_ENV: str = "development"
    APP_DEBUG: bool = False
    SECRET_KEY: str = ""
    ALLOWED_ORIGINS: str = ""
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    REDIS_PASSWORD: str = "changeme"
    REDIS_URL: str = "redis://redis:6379/0"
    DATABASE_URL: str = "sqlite+aiosqlite:////app/data/db/fakecheck.db"

    UPLOAD_DIR: str = "/app/data/videos"
    FRAMES_DIR: str = "/app/data/frames"
    MAX_VIDEO_SIZE_MB: int = 100
    MAX_VIDEO_DURATION_SEC: int = 600
    FRAMES_PER_VIDEO: int = 8
    FRAME_QUALITY: int = 85
    MOCK_MODE: bool = False
    
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_WEBHOOK_URL: str = ""
    USE_POLLING: bool = True
    
    SIGHTENGINE_API_USER: str = ""
    SIGHTENGINE_API_SECRET: str = ""
    
    RAPIDAPI_KEY: str = ""
    START_SITE_PASSWORD: str = ""
    MAILTRAP_API_TOKEN: str = ""

    ADMIN_EMAIL: str = "admin@example.com"
    ADMIN_PASSWORD: str = "admin123456"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8', extra='ignore')

    @property
    def redis_url_with_auth(self) -> str:
        """Get Redis URL with password authentication"""
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@redis:6379/0"
        return self.REDIS_URL

    @property
    def cors_origins(self) -> List[str]:
        origins = [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]
        capacitor_origins = ["capacitor://localhost", "http://localhost", "http://localhost:3000"]
        for co in capacitor_origins:
            if co not in origins:
                origins.append(co)
        return origins

@lru_cache
def get_settings() -> Settings:
    return Settings()
