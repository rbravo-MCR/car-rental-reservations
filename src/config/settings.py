"""
Application Settings
Configuración centralizada usando pydantic-settings
"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application Settings
    Carga configuración desde variables de entorno y .env file
    """

    # Database
    database_url: str = "sqlite+aiosqlite:///./car_rental.db"
    database_echo: bool = False
    database_pool_size: int = 5
    database_max_overflow: int = 10
    database_pool_recycle: int = 3600

    # Stripe
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""

    # Receipts
    receipts_output_dir: str = "./receipts"

    # Suppliers
    localiza_api_url: str = ""
    localiza_api_key: str = ""
    localiza_api_secret: str = ""

    # Application
    app_name: str = "Car Rental Reservations"
    app_version: str = "1.0.0"
    debug: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    """
    Obtener instancia singleton de Settings
    Cached para evitar re-leer archivo .env en cada llamada
    """
    return Settings()
