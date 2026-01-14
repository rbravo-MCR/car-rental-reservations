"""
Application Settings
Configuración centralizada usando pydantic-settings
"""
from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application Settings
    Carga configuración desde variables de entorno y .env file

    Soporta múltiples archivos de entorno con prioridad:
    1. Variables de entorno del sistema (mayor prioridad)
    2. .env.local (no versionado, para desarrollo local)
    3. .env (versionado, valores por defecto)
    """

    # Application
    app_name: str = Field(default="Car Rental Reservations", description="Nombre de la aplicación")
    app_version: str = Field(default="1.0.0", description="Versión de la aplicación")
    environment: Literal["development", "staging", "production"] = Field(
        default="development", description="Entorno de ejecución"
    )
    debug: bool = Field(default=False, description="Modo debug")
    log_level: str = Field(default="INFO", description="Nivel de logging")

    # Server
    host: str = Field(default="0.0.0.0", description="Host del servidor")
    port: int = Field(default=8000, description="Puerto del servidor", ge=1, le=65535)
    workers: int = Field(default=4, description="Número de workers", ge=1)

    # Database
    database_url: str = Field(
        default="sqlite+aiosqlite:///./car_rental.db",
        description="URL de conexión a la base de datos"
    )
    database_echo: bool = Field(
        default=False, description="Activar logging de SQL queries"
    )
    database_pool_size: int = Field(
        default=5, description="Tamaño del pool de conexiones", ge=1
    )
    database_max_overflow: int = Field(
        default=10, description="Máximo overflow del pool", ge=0
    )
    database_pool_recycle: int = Field(
        default=3600, description="Tiempo de reciclado de conexiones (segundos)", ge=1
    )

    # Redis
    redis_url: str = Field(
        default="redis://localhost:6379/0", description="URL de conexión a Redis"
    )
    redis_max_connections: int = Field(
        default=50, description="Máximo de conexiones a Redis", ge=1
    )

    # Stripe
    stripe_secret_key: str = Field(default="", description="Stripe secret key")
    stripe_public_key: str = Field(default="", description="Stripe public key")
    stripe_webhook_secret: str = Field(default="", description="Stripe webhook secret")

    # Receipts
    receipts_output_dir: str = Field(
        default="./receipts", description="Directorio de salida para recibos"
    )

    # Suppliers - Localiza
    localiza_api_key: str = Field(default="", description="Localiza API key")
    localiza_api_secret: str = Field(default="", description="Localiza API secret")
    localiza_base_url: str = Field(
        default="", description="Localiza API base URL"
    )

    # Suppliers - Europcar
    europcar_username: str = Field(default="", description="Europcar username")
    europcar_password: str = Field(default="", description="Europcar password")
    europcar_base_url: str = Field(default="", description="Europcar API base URL")

    # Suppliers - Rently
    rently_client_id: str = Field(default="", description="Rently client ID")
    rently_client_secret: str = Field(default="", description="Rently client secret")
    rently_base_url: str = Field(default="", description="Rently API base URL")

    # Security
    secret_key: str = Field(
        default="your-secret-key-change-this-in-production-min-32-chars",
        description="Secret key for JWT tokens",
        min_length=32,
    )
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(
        default=30, description="Tiempo de expiración del token (minutos)", ge=1
    )

    # CORS
    allowed_origins: str = Field(
        default="http://localhost:3000,http://localhost:8000",
        description="Orígenes permitidos para CORS (separados por comas)"
    )

    # Idempotency
    idempotency_ttl_days: int = Field(
        default=7, description="TTL de claves de idempotencia (días)", ge=1
    )

    # Rate Limiting
    rate_limit_per_minute: int = Field(
        default=60, description="Límite de requests por minuto", ge=1
    )
    rate_limit_per_hour: int = Field(
        default=1000, description="Límite de requests por hora", ge=1
    )

    # Outbox Worker
    outbox_batch_size: int = Field(
        default=10, description="Tamaño del batch para procesar eventos", ge=1
    )
    outbox_poll_interval_seconds: int = Field(
        default=5, description="Intervalo de polling del outbox (segundos)", ge=1
    )
    outbox_max_retries: int = Field(
        default=5, description="Máximo de reintentos para eventos", ge=0
    )
    outbox_retry_delay_seconds: int = Field(
        default=60, description="Delay entre reintentos (segundos)", ge=1
    )

    # Monitoring
    enable_metrics: bool = Field(default=True, description="Habilitar métricas")
    metrics_port: int = Field(
        default=9090, description="Puerto para métricas", ge=1, le=65535
    )

    model_config = SettingsConfigDict(
        env_file=(".env", ".env.local"),  # Múltiples archivos, .env.local tiene prioridad
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Ignorar variables extra no definidas
    )

    @field_validator("allowed_origins")
    @classmethod
    def parse_allowed_origins(cls, v: str) -> str:
        """Validar que allowed_origins sea una lista válida de URLs"""
        if not v:
            return v
        # Separar por comas y validar que no estén vacías
        origins = [origin.strip() for origin in v.split(",")]
        if not all(origins):
            raise ValueError("allowed_origins no puede contener valores vacíos")
        return v

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """Validar que secret_key no sea el valor por defecto en producción"""
        if len(v) < 32:
            raise ValueError("secret_key debe tener al menos 32 caracteres")
        return v

    @property
    def is_production(self) -> bool:
        """Verificar si está en modo producción"""
        return self.environment == "production"

    @property
    def is_development(self) -> bool:
        """Verificar si está en modo desarrollo"""
        return self.environment == "development"

    @property
    def cors_origins_list(self) -> list[str]:
        """Obtener lista de orígenes CORS permitidos"""
        return [origin.strip() for origin in self.allowed_origins.split(",")]


@lru_cache
def get_settings() -> Settings:
    """
    Obtener instancia singleton de Settings
    Cached para evitar re-leer archivo .env en cada llamada

    Returns:
        Settings: Instancia singleton de configuración
    """
    return Settings()
