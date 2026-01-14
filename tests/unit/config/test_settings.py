"""
Unit tests for Settings configuration and .env file loading
"""
import os
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from src.config.settings import Settings, get_settings


class TestSettingsDefaults:
    """Test default values when no .env file is present"""

    @patch.dict(os.environ, {}, clear=True)
    def test_default_application_settings(self) -> None:
        """Test default application settings"""
        settings = Settings(_env_file=None)  # Don't load .env file

        assert settings.app_name == "Car Rental Reservations"
        assert settings.app_version == "1.0.0"
        assert settings.environment == "development"
        assert settings.debug is False
        assert settings.log_level == "INFO"

    @patch.dict(os.environ, {}, clear=True)
    def test_default_server_settings(self) -> None:
        """Test default server settings"""
        settings = Settings(_env_file=None)

        assert settings.host == "0.0.0.0"
        assert settings.port == 8000
        assert settings.workers == 4

    @patch.dict(os.environ, {}, clear=True)
    def test_default_database_settings(self) -> None:
        """Test default database settings"""
        settings = Settings(_env_file=None)

        assert settings.database_url == "sqlite+aiosqlite:///./car_rental.db"
        assert settings.database_echo is False
        assert settings.database_pool_size == 5
        assert settings.database_max_overflow == 10
        assert settings.database_pool_recycle == 3600

    @patch.dict(os.environ, {}, clear=True)
    def test_default_redis_settings(self) -> None:
        """Test default Redis settings"""
        settings = Settings(_env_file=None)

        assert settings.redis_url == "redis://localhost:6379/0"
        assert settings.redis_max_connections == 50

    @patch.dict(os.environ, {}, clear=True)
    def test_default_stripe_settings(self) -> None:
        """Test default Stripe settings"""
        settings = Settings(_env_file=None)

        assert settings.stripe_secret_key == ""
        assert settings.stripe_public_key == ""
        assert settings.stripe_webhook_secret == ""

    @patch.dict(os.environ, {}, clear=True)
    def test_default_security_settings(self) -> None:
        """Test default security settings"""
        settings = Settings(_env_file=None)

        assert len(settings.secret_key) >= 32
        assert settings.algorithm == "HS256"
        assert settings.access_token_expire_minutes == 30


class TestSettingsEnvFileLoading:
    """Test loading settings from .env file"""

    def test_settings_loads_from_env_file(self) -> None:
        """Test that settings are loaded from .env file"""
        settings = Settings()

        # These values come from .env file
        assert settings.app_name is not None
        assert settings.database_url is not None

    @patch.dict(os.environ, {"APP_NAME": "Test App"}, clear=False)
    def test_env_vars_override_env_file(self) -> None:
        """Test that environment variables override .env file"""
        settings = Settings()

        # Environment variable should override .env file
        assert settings.app_name == "Test App"

    @patch.dict(os.environ, {"DATABASE_POOL_SIZE": "20"}, clear=False)
    def test_env_vars_type_conversion(self) -> None:
        """Test that environment variables are properly converted to correct types"""
        settings = Settings()

        assert isinstance(settings.database_pool_size, int)
        assert settings.database_pool_size == 20

    @patch.dict(os.environ, {"DEBUG": "true"}, clear=False)
    def test_boolean_env_vars(self) -> None:
        """Test boolean environment variables"""
        settings = Settings()

        assert isinstance(settings.debug, bool)
        assert settings.debug is True


class TestSettingsValidation:
    """Test settings validation"""

    @patch.dict(os.environ, {"PORT": "99999"}, clear=False)
    def test_port_validation_max(self) -> None:
        """Test that port validation rejects values above 65535"""
        with pytest.raises(ValidationError) as exc_info:
            Settings(_env_file=None)

        assert "port" in str(exc_info.value).lower()

    @patch.dict(os.environ, {"PORT": "0"}, clear=False)
    def test_port_validation_min(self) -> None:
        """Test that port validation rejects values below 1"""
        with pytest.raises(ValidationError) as exc_info:
            Settings(_env_file=None)

        assert "port" in str(exc_info.value).lower()

    @patch.dict(os.environ, {"SECRET_KEY": "short"}, clear=False)
    def test_secret_key_min_length(self) -> None:
        """Test that secret_key must be at least 32 characters"""
        with pytest.raises(ValidationError) as exc_info:
            Settings(_env_file=None)

        assert "secret_key" in str(exc_info.value).lower()

    @patch.dict(os.environ, {"DATABASE_POOL_SIZE": "0"}, clear=False)
    def test_pool_size_validation(self) -> None:
        """Test that pool size must be at least 1"""
        with pytest.raises(ValidationError) as exc_info:
            Settings(_env_file=None)

        assert "database_pool_size" in str(exc_info.value).lower()

    @patch.dict(os.environ, {"ENVIRONMENT": "invalid"}, clear=False)
    def test_environment_literal_validation(self) -> None:
        """Test that environment must be one of allowed values"""
        with pytest.raises(ValidationError) as exc_info:
            Settings(_env_file=None)

        error_str = str(exc_info.value).lower()
        assert "environment" in error_str


class TestSettingsFieldValidators:
    """Test custom field validators"""

    @patch.dict(
        os.environ,
        {
            "ALLOWED_ORIGINS": "http://localhost:3000,http://localhost:8000",
            "SECRET_KEY": "a" * 32,
        },
        clear=True,
    )
    def test_allowed_origins_validator(self) -> None:
        """Test allowed_origins custom validator"""
        settings = Settings(_env_file=None)

        assert settings.allowed_origins == "http://localhost:3000,http://localhost:8000"

    @patch.dict(
        os.environ,
        {"ALLOWED_ORIGINS": "http://localhost:3000,,http://localhost:8000", "SECRET_KEY": "a" * 32},
        clear=True,
    )
    def test_allowed_origins_empty_value_validation(self) -> None:
        """Test that allowed_origins rejects empty values"""
        with pytest.raises(ValidationError) as exc_info:
            Settings(_env_file=None)

        assert "allowed_origins" in str(exc_info.value).lower()


class TestSettingsProperties:
    """Test computed properties"""

    @patch.dict(os.environ, {"ENVIRONMENT": "production", "SECRET_KEY": "a" * 32}, clear=True)
    def test_is_production_property(self) -> None:
        """Test is_production property"""
        settings = Settings(_env_file=None)

        assert settings.is_production is True
        assert settings.is_development is False

    @patch.dict(os.environ, {"ENVIRONMENT": "development", "SECRET_KEY": "a" * 32}, clear=True)
    def test_is_development_property(self) -> None:
        """Test is_development property"""
        settings = Settings(_env_file=None)

        assert settings.is_development is True
        assert settings.is_production is False

    @patch.dict(
        os.environ,
        {
            "ALLOWED_ORIGINS": "http://localhost:3000,http://localhost:8000,http://localhost:5000",
            "SECRET_KEY": "a" * 32,
        },
        clear=True,
    )
    def test_cors_origins_list_property(self) -> None:
        """Test cors_origins_list property returns list"""
        settings = Settings(_env_file=None)

        origins = settings.cors_origins_list
        assert isinstance(origins, list)
        assert len(origins) == 3
        assert "http://localhost:3000" in origins
        assert "http://localhost:8000" in origins
        assert "http://localhost:5000" in origins

    @patch.dict(
        os.environ,
        {
            "ALLOWED_ORIGINS": " http://localhost:3000 , http://localhost:8000 ",
            "SECRET_KEY": "a" * 32,
        },
        clear=True,
    )
    def test_cors_origins_list_strips_whitespace(self) -> None:
        """Test that cors_origins_list strips whitespace"""
        settings = Settings(_env_file=None)

        origins = settings.cors_origins_list
        assert all(origin == origin.strip() for origin in origins)


class TestGetSettingsSingleton:
    """Test get_settings singleton function"""

    def test_get_settings_returns_settings_instance(self) -> None:
        """Test that get_settings returns Settings instance"""
        settings = get_settings()

        assert isinstance(settings, Settings)

    def test_get_settings_returns_same_instance(self) -> None:
        """Test that get_settings returns cached instance"""
        # Clear cache first
        get_settings.cache_clear()

        settings1 = get_settings()
        settings2 = get_settings()

        # Should be the exact same instance (singleton pattern)
        assert settings1 is settings2

    def test_get_settings_cache_clear(self) -> None:
        """Test that cache can be cleared"""
        get_settings.cache_clear()

        settings1 = get_settings()
        get_settings.cache_clear()
        settings2 = get_settings()

        # After cache clear, should be different instances
        assert settings1 is not settings2


class TestSettingsSupplierConfiguration:
    """Test supplier-specific configuration"""

    @patch.dict(os.environ, {}, clear=True)
    def test_localiza_settings_defaults(self) -> None:
        """Test Localiza supplier settings defaults"""
        settings = Settings(_env_file=None)

        assert settings.localiza_api_key == ""
        assert settings.localiza_api_secret == ""
        assert settings.localiza_base_url == ""

    @patch.dict(os.environ, {}, clear=True)
    def test_europcar_settings_defaults(self) -> None:
        """Test Europcar supplier settings defaults"""
        settings = Settings(_env_file=None)

        assert settings.europcar_username == ""
        assert settings.europcar_password == ""
        assert settings.europcar_base_url == ""

    @patch.dict(os.environ, {}, clear=True)
    def test_rently_settings_defaults(self) -> None:
        """Test Rently supplier settings defaults"""
        settings = Settings(_env_file=None)

        assert settings.rently_client_id == ""
        assert settings.rently_client_secret == ""
        assert settings.rently_base_url == ""


class TestSettingsOutboxConfiguration:
    """Test outbox worker configuration"""

    @patch.dict(os.environ, {}, clear=True)
    def test_outbox_settings_defaults(self) -> None:
        """Test outbox worker settings defaults"""
        settings = Settings(_env_file=None)

        assert settings.outbox_batch_size == 10
        assert settings.outbox_poll_interval_seconds == 5
        assert settings.outbox_max_retries == 5
        assert settings.outbox_retry_delay_seconds == 60

    @patch.dict(os.environ, {"OUTBOX_BATCH_SIZE": "0"}, clear=False)
    def test_outbox_batch_size_validation(self) -> None:
        """Test that outbox_batch_size must be at least 1"""
        with pytest.raises(ValidationError) as exc_info:
            Settings(_env_file=None)

        assert "outbox_batch_size" in str(exc_info.value).lower()


class TestSettingsMonitoringConfiguration:
    """Test monitoring and metrics configuration"""

    @patch.dict(os.environ, {}, clear=True)
    def test_monitoring_settings_defaults(self) -> None:
        """Test monitoring settings defaults"""
        settings = Settings(_env_file=None)

        assert settings.enable_metrics is True
        assert settings.metrics_port == 9090

    @patch.dict(os.environ, {"ENABLE_METRICS": "false"}, clear=False)
    def test_metrics_can_be_disabled(self) -> None:
        """Test that metrics can be disabled"""
        settings = Settings()

        assert settings.enable_metrics is False


class TestSettingsCaseInsensitivity:
    """Test case-insensitive environment variable loading"""

    @patch.dict(os.environ, {"app_name": "Test App Lower"}, clear=False)
    def test_lowercase_env_vars(self) -> None:
        """Test that lowercase env vars are recognized"""
        settings = Settings()

        # case_sensitive=False should make this work
        assert settings.app_name == "Test App Lower"

    @patch.dict(os.environ, {"APP_NAME": "Test App Upper"}, clear=False)
    def test_uppercase_env_vars(self) -> None:
        """Test that uppercase env vars are recognized"""
        settings = Settings()

        assert settings.app_name == "Test App Upper"


class TestSettingsRateLimiting:
    """Test rate limiting configuration"""

    @patch.dict(os.environ, {}, clear=True)
    def test_rate_limiting_defaults(self) -> None:
        """Test rate limiting defaults"""
        settings = Settings(_env_file=None)

        assert settings.rate_limit_per_minute == 60
        assert settings.rate_limit_per_hour == 1000

    @patch.dict(os.environ, {"RATE_LIMIT_PER_MINUTE": "0"}, clear=False)
    def test_rate_limit_validation(self) -> None:
        """Test that rate limits must be at least 1"""
        with pytest.raises(ValidationError) as exc_info:
            Settings(_env_file=None)

        assert "rate_limit_per_minute" in str(exc_info.value).lower()
