"""
Database connection and session management
"""

import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from sqlalchemy import create_engine, pool
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import Session, sessionmaker
from loguru import logger

from src.database.models import Base


class DatabaseManager:
    """Manages database connections and sessions"""
    
    def __init__(self, database_url: Optional[str] = None):
        self.database_url = database_url or os.getenv("DATABASE_URL")
        
        if not self.database_url:
            raise ValueError("DATABASE_URL not provided")
        
        # Convert to async URL if needed
        if self.database_url.startswith("postgresql://"):
            self.async_database_url = self.database_url.replace(
                "postgresql://", "postgresql+asyncpg://"
            )
        else:
            self.async_database_url = self.database_url
        
        # Create async engine
        self.async_engine = create_async_engine(
            self.async_database_url,
            echo=os.getenv("DEBUG", "false").lower() == "true",
            pool_size=20,
            max_overflow=10,
            pool_pre_ping=True,
            pool_recycle=3600
        )
        
        # Create sync engine for migrations
        self.sync_engine = create_engine(
            self.database_url,
            echo=os.getenv("DEBUG", "false").lower() == "true",
            poolclass=pool.NullPool
        )
        
        # Session factories
        self.async_session_factory = async_sessionmaker(
            self.async_engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        self.sync_session_factory = sessionmaker(
            self.sync_engine,
            expire_on_commit=False
        )
        
        logger.info("Database manager initialized")
    
    async def create_tables(self):
        """Create all database tables"""
        try:
            async with self.async_engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating tables: {e}")
            raise
    
    async def drop_tables(self):
        """Drop all database tables (use with caution!)"""
        try:
            async with self.async_engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
            logger.warning("All database tables dropped")
        except Exception as e:
            logger.error(f"Error dropping tables: {e}")
            raise
    
    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get an async database session"""
        async with self.async_session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    def get_sync_session(self) -> Session:
        """Get a sync database session (for scripts/migrations)"""
        return self.sync_session_factory()
    
    async def close(self):
        """Close all database connections"""
        await self.async_engine.dispose()
        self.sync_engine.dispose()
        logger.info("Database connections closed")
    
    async def log_trade(self, trade_data: dict) -> int:
        """Log a trade to the database"""
        from src.database.models import Trade
        
        async with self.get_session() as session:
            trade = Trade(**trade_data)
            session.add(trade)
            await session.commit()
            await session.refresh(trade)
            return trade.id
    
    async def log_signal(self, signal_data: dict) -> int:
        """Log a signal to the database"""
        from src.database.models import Signal
        
        async with self.get_session() as session:
            signal = Signal(**signal_data)
            session.add(signal)
            await session.commit()
            await session.refresh(signal)
            return signal.id
    
    async def log_decision(self, decision_data: dict) -> int:
        """Log a trading decision"""
        from src.database.models import DecisionLog
        
        async with self.get_session() as session:
            decision = DecisionLog(**decision_data)
            session.add(decision)
            await session.commit()
            await session.refresh(decision)
            return decision.id
    
    async def log_error(self, error_message: str, context: Optional[dict] = None):
        """Log an error as an alert"""
        from src.database.models import Alert
        
        async with self.get_session() as session:
            alert = Alert(
                alert_type="ERROR",
                severity="HIGH",
                title="Trading Bot Error",
                message=error_message,
                alert_metadata=context or {}
            )
            session.add(alert)
            await session.commit()
    
    async def log_trades(self, trades: list) -> list:
        """Log multiple trades"""
        from src.database.models import Trade
        
        async with self.get_session() as session:
            trade_ids = []
            for trade_data in trades:
                trade = Trade(**trade_data)
                session.add(trade)
                await session.flush()
                trade_ids.append(trade.id)
            await session.commit()
            return trade_ids
    
    async def get_recent_signals(self, symbol: Optional[str] = None, limit: int = 100):
        """Get recent signals from the database"""
        from sqlalchemy import select, desc
        from src.database.models import Signal
        
        async with self.get_session() as session:
            query = select(Signal).order_by(desc(Signal.created_at)).limit(limit)
            
            if symbol:
                query = query.where(Signal.symbol == symbol)
            
            result = await session.execute(query)
            return result.scalars().all()
    
    async def get_open_trades(self):
        """Get all open trades"""
        from sqlalchemy import select
        from src.database.models import Trade
        
        async with self.get_session() as session:
            query = select(Trade).where(
                Trade.status.in_(["PENDING", "SUBMITTED", "FILLED", "PARTIAL"])
            )
            result = await session.execute(query)
            return result.scalars().all()
    
    async def update_trade_status(self, trade_id: int, status: str, **kwargs):
        """Update trade status and related fields"""
        from sqlalchemy import update
        from src.database.models import Trade
        
        async with self.get_session() as session:
            stmt = update(Trade).where(Trade.id == trade_id).values(
                status=status,
                **kwargs
            )
            await session.execute(stmt)
            await session.commit()
    
    async def save_market_snapshot(self, snapshot_data: dict):
        """Save market snapshot"""
        from src.database.models import MarketSnapshot
        
        async with self.get_session() as session:
            snapshot = MarketSnapshot(**snapshot_data)
            session.add(snapshot)
            await session.commit()
    
    async def get_strategy_performance(self, strategy_name: str, days: int = 30):
        """Get strategy performance metrics"""
        from sqlalchemy import select, desc
        from datetime import datetime, timedelta
        from src.database.models import StrategyPerformance
        
        async with self.get_session() as session:
            cutoff_date = datetime.now() - timedelta(days=days)
            query = select(StrategyPerformance).where(
                StrategyPerformance.strategy_name == strategy_name,
                StrategyPerformance.date >= cutoff_date
            ).order_by(desc(StrategyPerformance.date))
            
            result = await session.execute(query)
            return result.scalars().all()