"""
Database configuration
SQLAlchemy async engine y session factory
"""

from collections.abc import AsyncGenerator

from src.config.settings import get_settings
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base

settings = get_settings()

# Crear engine async
async_engine = create_async_engine(
    settings.database_url,
    echo=settings.database_echo,
    pool_size=settings.database_pool_size,
    max_overflow=settings.database_max_overflow,
    pool_recycle=settings.database_pool_recycle,
    pool_pre_ping=True,  # Verificar conexión antes de usar
)

# Session factory
async_session_factory = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Base para models
Base = declarative_base()


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    #Dependency para obtener sesión de BD
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()
