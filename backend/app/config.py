import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Controle Financeiro Pessoal"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "finance_super_secret_key_change_me_in_production_123456789")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 dias
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./finance.db")
    
    model_config = SettingsConfigDict(case_sensitive=True)

settings = Settings()

