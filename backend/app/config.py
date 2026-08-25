import os
from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Controle Financeiro Pessoal"
    ENVIRONMENT: str = "development" # 'development' ou 'production'
    
    SECRET_KEY: str = "finance_default_secret_key_change_in_production_987654321"
    ALGORITHM: str = "HS256"
    # Default to 7 days (in minutes). This value can be overridden via .env or environment variables.
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days
    ADMIN_SECRET_PASSWORD: str = ""
    DATABASE_URL: str = "sqlite:///./finance.db"
    
    # CORS: lista de origens autorizadas (pode ser string separada por vírgula no .env)
    CORS_ORIGINS: Union[List[str], str] = "http://localhost:8000,http://127.0.0.1:8000"

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

if settings.ENVIRONMENT == "production":
    if not settings.SECRET_KEY or settings.SECRET_KEY == "finance_default_secret_key_change_in_production_987654321":
        raise RuntimeError("SECRET_KEY deve ser configurada com um valor forte em produção.")
