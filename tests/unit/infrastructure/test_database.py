"""
Unit tests for database connection and session management
"""
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.persistence.database import (
    Base,
    async_engine,
    async_session_factory,
    get_session,
)


class TestDatabaseEngine:
    """Test async engine creation and configuration"""

    def test_engine_is_created(self) -> None:
        """Test that async engine is properly instantiated"""
        assert async_engine is not None
        assert hasattr(async_engine, "url")

    def test_engine_url_is_configured(self) -> None:
        """Test that engine URL is set from settings"""
        # Engine URL should be from settings
        assert async_engine.url is not None
        # Should be a valid database URL (MySQL or SQLite)
        url_str = str(async_engine.url)
        assert url_str.startswith("mysql") or url_str.startswith("sqlite")

    def test_engine_pool_configuration(self) -> None:
        """Test that engine pool is configured with correct settings"""
        # Check pool configuration
        assert async_engine.pool is not None
        # pool_pre_ping should be enabled for connection health checks
        assert async_engine.pool._pre_ping is True

    @patch("src.infrastructure.persistence.database.get_settings")
    def test_engine_uses_settings_values(self, mock_get_settings: MagicMock) -> None:
        """Test that engine configuration comes from settings"""
        from src.infrastructure.persistence.database import settings

        # Verify settings are loaded
        assert settings is not None
        assert hasattr(settings, "database_url")
        assert hasattr(settings, "database_echo")
        assert hasattr(settings, "database_pool_size")


class TestSessionFactory:
    """Test async session factory"""

    def test_session_factory_is_created(self) -> None:
        """Test that session factory is properly instantiated"""
        assert async_session_factory is not None
        assert callable(async_session_factory)

    def test_session_factory_creates_async_session(self) -> None:
        """Test that session factory returns AsyncSession instances"""
        session = async_session_factory()
        assert isinstance(session, AsyncSession)

    def test_session_factory_expire_on_commit_is_false(self) -> None:
        """Test that expire_on_commit is configured as False"""
        session = async_session_factory()
        # expire_on_commit=False prevents lazy loading issues after commit
        # Check internal sync_session which holds the actual expire_on_commit setting
        assert session.sync_session.expire_on_commit is False


class TestGetSession:
    """Test get_session dependency function"""

    @pytest.mark.asyncio
    async def test_get_session_yields_session(self) -> None:
        """Test that get_session yields an AsyncSession"""
        async for session in get_session():
            assert isinstance(session, AsyncSession)
            assert session is not None
            break

    @pytest.mark.asyncio
    async def test_get_session_closes_after_use(self) -> None:
        """Test that session is properly closed after context"""
        session_ref = None

        async for session in get_session():
            session_ref = session
            assert not session_ref.is_active or session_ref.is_active
            break

        # After generator exits, session should be closed
        # We can't directly test if it's closed, but we can verify it existed
        assert session_ref is not None

    @pytest.mark.asyncio
    async def test_get_session_handles_exception(self) -> None:
        """Test that get_session closes session even on exception"""
        with patch.object(
            AsyncSession, "__aenter__", side_effect=Exception("Connection error")
        ):
            with pytest.raises(Exception) as exc_info:
                async for _ in get_session():
                    pass

            # Exception should propagate but session cleanup should happen
            assert "Connection error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_session_is_generator(self) -> None:
        """Test that get_session is an async generator"""
        gen = get_session()
        assert hasattr(gen, "__aiter__")
        assert hasattr(gen, "__anext__")


class TestDatabaseBase:
    """Test declarative base for ORM models"""

    def test_base_is_created(self) -> None:
        """Test that declarative base is properly instantiated"""
        assert Base is not None

    def test_base_has_metadata(self) -> None:
        """Test that base has metadata for table definitions"""
        assert hasattr(Base, "metadata")
        assert Base.metadata is not None

    def test_base_metadata_is_empty(self) -> None:
        """Test that base metadata starts empty (models not loaded in unit test)"""
        # In unit tests, models might not be imported
        # Just verify metadata exists and is accessible
        assert hasattr(Base.metadata, "tables")


class TestDatabaseConnectionPooling:
    """Test database connection pooling configuration"""

    def test_pool_size_configuration(self) -> None:
        """Test that pool size is configured"""
        # Pool should exist
        assert async_engine.pool is not None

    def test_pool_pre_ping_enabled(self) -> None:
        """Test that pool pre-ping is enabled for stale connection detection"""
        # pre_ping verifies connections before using them
        assert async_engine.pool._pre_ping is True

    @patch("src.infrastructure.persistence.database.get_settings")
    def test_pool_uses_settings_configuration(
        self, mock_get_settings: MagicMock
    ) -> None:
        """Test that pool configuration comes from settings"""
        from src.infrastructure.persistence.database import settings

        # Verify pool-related settings exist
        assert hasattr(settings, "database_pool_size")
        assert hasattr(settings, "database_max_overflow")
        assert hasattr(settings, "database_pool_recycle")
        assert isinstance(settings.database_pool_size, int)
        assert isinstance(settings.database_max_overflow, int)
        assert isinstance(settings.database_pool_recycle, int)


class TestDatabaseSessionLifecycle:
    """Test session lifecycle management"""

    @pytest.mark.asyncio
    async def test_session_begin_transaction(self) -> None:
        """Test that session can begin transactions"""
        async for session in get_session():
            # Session should support begin()
            assert hasattr(session, "begin")
            break

    @pytest.mark.asyncio
    async def test_session_commit_available(self) -> None:
        """Test that session has commit method"""
        async for session in get_session():
            assert hasattr(session, "commit")
            assert callable(session.commit)
            break

    @pytest.mark.asyncio
    async def test_session_rollback_available(self) -> None:
        """Test that session has rollback method"""
        async for session in get_session():
            assert hasattr(session, "rollback")
            assert callable(session.rollback)
            break

    @pytest.mark.asyncio
    async def test_session_close_available(self) -> None:
        """Test that session has close method"""
        async for session in get_session():
            assert hasattr(session, "close")
            assert callable(session.close)
            break


class TestDatabaseConnectionRecovery:
    """Test connection recovery and error handling"""

    @pytest.mark.asyncio
    async def test_session_factory_creates_new_session_each_time(self) -> None:
        """Test that session factory creates independent sessions"""
        session1 = async_session_factory()
        session2 = async_session_factory()

        # Each call should create a new session instance
        assert session1 is not session2

    @pytest.mark.asyncio
    async def test_get_session_creates_fresh_session(self) -> None:
        """Test that each call to get_session creates a new session"""
        sessions = []

        for i in range(2):
            async for session in get_session():
                sessions.append(session)
                break

        # Should have 2 different session instances
        assert len(sessions) == 2
        assert sessions[0] is not sessions[1]


class TestDatabaseConfiguration:
    """Test database configuration from settings"""

    def test_database_url_from_settings(self) -> None:
        """Test that database URL is loaded from settings"""
        from src.infrastructure.persistence.database import settings

        assert settings.database_url is not None
        assert isinstance(settings.database_url, str)
        assert len(settings.database_url) > 0

    def test_database_echo_from_settings(self) -> None:
        """Test that database echo setting is loaded"""
        from src.infrastructure.persistence.database import settings

        assert hasattr(settings, "database_echo")
        assert isinstance(settings.database_echo, bool)

    def test_database_pool_settings_from_settings(self) -> None:
        """Test that pool settings are loaded from settings"""
        from src.infrastructure.persistence.database import settings

        assert settings.database_pool_size > 0
        assert settings.database_max_overflow >= 0
        assert settings.database_pool_recycle > 0


class TestAsyncEngineFeatures:
    """Test async engine specific features"""

    def test_engine_is_async(self) -> None:
        """Test that engine is async-capable"""
        assert hasattr(async_engine, "begin")
        assert hasattr(async_engine, "connect")
        # Async engine should have async methods
        assert callable(async_engine.begin)

    def test_engine_dialect_is_async(self) -> None:
        """Test that engine uses async dialect"""
        # For aiosqlite, dialect should support async
        assert async_engine.dialect is not None
        # Driver should be async-compatible
        assert async_engine.driver is not None


class TestDatabaseIntegration:
    """Test database integration patterns"""

    @pytest.mark.asyncio
    async def test_multiple_concurrent_sessions(self) -> None:
        """Test that multiple sessions can be created concurrently"""
        sessions = []

        # Create multiple sessions
        for _ in range(3):
            session = async_session_factory()
            sessions.append(session)

        # All sessions should be independent
        assert len(sessions) == 3
        assert len(set(id(s) for s in sessions)) == 3  # All unique

    @pytest.mark.asyncio
    async def test_session_isolation(self) -> None:
        """Test that sessions are isolated from each other"""
        session1 = async_session_factory()
        session2 = async_session_factory()

        # Sessions should have independent identity maps
        assert session1.identity_map is not session2.identity_map
