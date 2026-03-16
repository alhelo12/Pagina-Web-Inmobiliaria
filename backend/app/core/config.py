"""
Core: Configuration

Configuración centralizada de la aplicación usando Pydantic BaseSettings.
Lee variables de entorno desde .env
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Configuración de la aplicación
    
    Todas las variables se leen desde .env
    Si no existen, se usan los valores por defecto.
    """
    
    # ==========================================
    # APLICACIÓN
    # ==========================================
    APP_NAME: str = "Inmobiliaria API"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"  # development, staging, production
    DEBUG: bool = True
    
    # ==========================================
    # BASE DE DATOS
    # ==========================================
    DATABASE_URL: str
    
    # Pool de conexiones
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_RECYCLE: int = 1800  # 30 minutos
    DB_POOL_PRE_PING: bool = True
    DB_ECHO: bool = False  # SQL logging
    
    # ==========================================
    # JWT / SEGURIDAD
    # ==========================================
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # ==========================================
    # CORS
    # ==========================================
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",  # Vite
        "http://localhost:3000",  # React/Next
    ]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list[str] = ["*"]
    CORS_ALLOW_HEADERS: list[str] = ["*"]
    
    # ==========================================
    # API
    # ==========================================
    API_PREFIX: str = ""  # Si quieres /api/v1
    DOCS_URL: str = "/docs"
    REDOC_URL: str = "/redoc"
    OPENAPI_URL: str = "/openapi.json"
    
    # ==========================================
    # PAGINACIÓN
    # ==========================================
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    # ==========================================
    # UPLOADS (futuro)
    # ==========================================
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE_MB: int = 10
    ALLOWED_IMAGE_EXTENSIONS: list[str] = [".jpg", ".jpeg", ".png", ".webp"]
    
    # ==========================================
    # EMAIL (futuro)
    # ==========================================
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: Optional[int] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM_EMAIL: Optional[str] = None
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# ==========================================
# INSTANCIA GLOBAL
# ==========================================

settings = Settings()


# ==========================================
# FUNCIONES DE UTILIDAD
# ==========================================

def is_production() -> bool:
    """Verificar si estamos en producción"""
    return settings.ENVIRONMENT == "production"


def is_development() -> bool:
    """Verificar si estamos en desarrollo"""
    return settings.ENVIRONMENT == "development"


def get_database_url() -> str:
    """Obtener URL de base de datos"""
    return settings.DATABASE_URL


def get_cors_origins() -> list[str]:
    """Obtener orígenes permitidos para CORS"""
    return settings.CORS_ORIGINS
