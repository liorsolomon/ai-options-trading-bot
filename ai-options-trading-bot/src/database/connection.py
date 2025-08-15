"""
Database connection management
"""

import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from loguru import logger

from .models import Base


class DatabaseManager:
    """Manages database connections and sessions"""
    
    def __init__(self, database_url: Optional[str] = None):
        """Initialize database manager
        
        Args:
            database_url: Database connection URL. If not provided, uses DATABASE_URL env var
        """
        self.database_url = database_url or os.getenv("DATABASE_URL")
        
        if not self.database_url:
            raise ValueError("DATABASE_URL not provided")
        
        # Convert postgres:// to postgresql:// for SQLAlchemy compatibility
        if self.database_url.startswith("postgres://"):
            self.database_url = self.database_url.replace("postgres://", "postgresql://", 1)
        
        # Create async engine
        self.engine = create_async_engine(
            self.database_url,
            echo=False,  # Set to True for SQL logging
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10
        )
        
        # Create session factory
        self.async_session = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    
    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get database session
        
        Yields:
            AsyncSession: Database session
        """
        async with self.async_session() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    async def create_tables(self):
        """Create all database tables"""
        try:
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating tables: {e}")
            raise
    
    async def drop_tables(self):
        """Drop all database tables"""
        try:
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
            logger.info("Database tables dropped successfully")
        except Exception as e:
            logger.error(f"Error dropping tables: {e}")
            raise
    
    async def close(self):
        """Close database connections"""
        await self.engine.dispose()
        logger.info("Database connections closed")
    
    async def test_connection(self) -> bool:
        """Test database connection
        
        Returns:
            bool: True if connection successful
        """
        try:
            async with self.get_session() as session:
                # Simple query to test connection
                from sqlalchemy import text
                result = await session.execute(text("SELECT 1"))
                return result.scalar() == 1
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False


# Singleton instance
_db_manager: Optional[DatabaseManager] = None


def get_db_manager() -> DatabaseManager:
    """Get database manager instance
    
    Returns:
        DatabaseManager: Database manager instance
    """
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager


async def init_database():
    """Initialize database"""
    db_manager = get_db_manager()
    await db_manager.create_tables()
    logger.info("Database initialized")