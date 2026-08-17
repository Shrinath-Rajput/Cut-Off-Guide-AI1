import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MONGODB_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    MONGODB_DATABASE: str = os.getenv("MONGO_DATABASE", "cutoffgrid")
    
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "supersecretkey_please_change_in_production")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

    FAST_TO_SMS_API_KEY: str = os.getenv("FAST_TO_SMS_API_KEY", "")
    OTP_MODE: str = os.getenv("OTP_MODE", "development")

    SMS_PROVIDER: str = (os.getenv("SMS_PROVIDER", "fast2sms") or "fast2sms").strip().lower()
    SMS_SENDER_ID: str = (os.getenv("SMS_SENDER_ID", "FSTSMS") or "FSTSMS").strip()
    SMS_ROUTE: str = (os.getenv("SMS_ROUTE", "q") or "q").strip().lower()
    SMS_TEMPLATE_ID: str = os.getenv("SMS_TEMPLATE_ID") or ""
    SMS_ENTITY_ID: str = (os.getenv("SMS_ENTITY_ID") or os.getenv("SMS_PE_ID") or "").strip()
    SMS_LANGUAGE: str = (os.getenv("SMS_LANGUAGE", "english") or "english").strip().lower()
    SMS_FLASH: str = (os.getenv("SMS_FLASH", "0") or "0").strip()

    OTP_TTL_SECONDS: int = int(os.getenv("OTP_TTL_SECONDS", "300"))
    
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:3000",
        "http://127.0.0.1:5173"
    ]

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
