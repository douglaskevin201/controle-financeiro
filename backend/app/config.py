import os
from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Controle Financeiro Pessoal"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development") # 'development' ou 'production'
    
    SECRET_KEY: str = os.getenv("SECRET_KEY", "finance_default_secret_key_change_in_production_987654321")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 365  # 1 year
    ADMIN_SECRET_PASSWORD: str = os.getenv("ADMIN_SECRET_PASSWORD", "06062026")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./finance.db")
    
    # CORS: lista de origens autorizadas (pode ser string separada por vírgula no .env)
    CORS_ORIGINS: Union[List[str], str] = os.getenv("CORS_ORIGINS", "http://localhost:8000,http://127.0.0.1:8000")

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            if v == "*":
                return ["*"]
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()
