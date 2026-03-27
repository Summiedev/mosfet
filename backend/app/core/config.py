from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App
    APP_NAME: str
    APP_ENV: str
    DEBUG: bool
    FRONTEND_URL: str

    # MongoDB
    MONGODB_URL: str
    MONGODB_DB_NAME: str

    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # OTP (Termii)
    INTERSWITCH_CLIENT_ID: str = ""
    INTERSWITCH_CLIENT_SECRET: str = ""
    INTERSWITCH_BASE_URL: str = "https://qa.interswitchng.com"
    OTP_EXPIRE_MINUTES: int = 10
    OTP_LENGTH: int = 6

    # Media storage — Cloudinary (free tier, no SDK needed, pure HTTP)
    CLOUDINARY_CLOUD_NAME: str = ""
    CLOUDINARY_API_KEY: str = ""
    CLOUDINARY_API_SECRET: str = ""
    CLOUDINARY_UPLOAD_PRESET: str = "radflow_frames"
    CLOUDINARY_FOLDER: str = "radflow/frames"

    # Max upload size in MB
    MEDIA_MAX_SIZE_MB: int = 10


    class Config:
        env_file = ".env"
        extra = "ignore"
        



@lru_cache()
def get_settings() -> Settings:
    
    return Settings()


settings = get_settings()
print(settings.FRONTEND_URL)