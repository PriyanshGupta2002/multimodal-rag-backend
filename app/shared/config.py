# Decompiled with PyLingual (https://pylingual.io)
# Internal filename: '/Users/priyansh/Projects/multimodal-rag/backend/app/shared/config.py'
# Bytecode version: 3.12.0rc2 (3531)
# Source timestamp: 2026-10-19 13:30:02 UTC (1792416602)

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int
    IMAGEKIT_PRIVATE_KEY: str
    IMAGEKIT_URL_ENDPOINT: str
    IMAGEKIT_PUBLIC_KEY: str
    REDIS_URL: str
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
