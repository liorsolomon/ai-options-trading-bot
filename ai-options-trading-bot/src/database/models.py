"""
Database models for the AI Options Trading Bot
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from sqlalchemy import (
    Column, String, Integer, Float, DateTime, Boolean, 
    ForeignKey, JSON, Text, Numeric, Index, UniqueConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()


class SignalType(str, Enum):
    CALL = "CALL"
    PUT = "PUT"
    IRON_CONDOR = "IRON_CONDOR"
    STRADDLE = "STRADDLE"
    STRANGLE = "STRANGLE"


class OrderStatus(str, Enum):
    PENDING = "PENDING"
    SUBMITTED = "SUBMITTED"
    FILLED = "FILLED"
    PARTIAL = "PARTIAL"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


class Signal(Base):
    """Historical signals with outcomes for pattern learning"""
    __tablename__ = "signals"
    
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, server_default=func.now())
    
    # Signal details
    symbol = Column(String(10), nullable=False, index=True)
    signal_type = Column(String(20), nullable=False)  # CALL, PUT, etc.
    confidence = Column(Float, nullable=False)  # 0.0 to 1.0
    
    # Market conditions at signal time
    underlying_price = Column(Numeric(10, 2))
    strike_price = Column(Numeric(10, 2))
    expiration_date = Column(DateTime)
    implied_volatility = Column(Float)
    volume = Column(Integer)
    open_interest = Column(Integer)
    
    # Greeks at signal time
    delta = Column(Float)
    gamma = Column(Float)
    theta = Column(Float)
    vega = Column(Float)
    
    # Technical indicators
    rsi = Column(Float)
    macd = Column(Float)
    bollinger_position = Column(Float)  # Position within bands
    volume_ratio = Column(Float)  # Current vs average volume
    
    # Sentiment scores
    news_sentiment = Column(Float)  # -1.0 to 1.0
    social_sentiment = Column(Float)  # -1.0 to 1.0
    options_flow_sentiment = Column(Float)  # Bullish/bearish flow
    
    # Strategy that generated the signal
    strategy_name = Column(String(50))
    strategy_params = Column(JSON)
    
    # Claude's analysis
    claude_recommendation = Column(Text)
    claude_confidence = Column(Float)
    claude_reasoning = Column(JSON)
    
    # Outcome tracking
    trade_executed = Column(Boolean, default=False)
    trade_id = Column(Integer, ForeignKey("trades.id"))
    
    # Success metrics (filled after trade completes)
    was_profitable = Column(Boolean)
    profit_loss = Column(Numeric(10, 2))
    profit_loss_percent = Column(Float)
    holding_period_hours = Column(Float)
    max_profit = Column(Numeric(10, 2))
    max_loss = Column(Numeric(10, 2))
    
    # Relationships
    trade = relationship("Trade", back_populates="signal", uselist=False)
    
    # Indexes for performance
    __table_args__ = (
        Index("idx_signal_symbol_date", "symbol", "created_at"),
        Index("idx_signal_profitable", "was_profitable", "profit_loss_percent"),
    )


class Trade(Base):
    """Executed trades with complete lifecycle tracking"""
    __tablename__ = "trades"
    
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Order details
    alpaca_order_id = Column(String(100), unique=True)
    symbol = Column(String(20), nullable=False, index=True)
    option_symbol = Column(String(50))  # Full OCC symbol
    order_type = Column(String(10))  # MARKET, LIMIT
    side = Column(String(10))  # BUY, SELL
    quantity = Column(Integer, nullable=False)
    
    # Pricing
    limit_price = Column(Numeric(10, 2))
    filled_price = Column(Numeric(10, 2))
    commission = Column(Numeric(10, 2), default=0)
    
    # Status tracking
    status = Column(String(20), nullable=False, index=True)
    submitted_at = Column(DateTime)
    filled_at = Column(DateTime)
    closed_at = Column(DateTime)
    
    # Position management
    stop_loss_price = Column(Numeric(10, 2))
    take_profit_price = Column(Numeric(10, 2))
    trailing_stop_percent = Column(Float)
    
    # Exit details
    exit_reason = Column(String(50))  # STOP_LOSS, TAKE_PROFIT, MANUAL, EXPIRED
    exit_price = Column(Numeric(10, 2))
    exit_order_id = Column(String(100))
    
    # Performance
    realized_pnl = Column(Numeric(10, 2))
    realized_pnl_percent = Column(Float)
    max_unrealized_profit = Column(Numeric(10, 2))
    max_unrealized_loss = Column(Numeric(10, 2))
    
    # Risk metrics
    position_size_percent = Column(Float)  # % of portfolio
    risk_amount = Column(Numeric(10, 2))  # Dollar risk
    risk_reward_ratio = Column(Float)
    
    # Relationships
    signal = relationship("Signal", back_populates="trade", uselist=False)
    position_updates = relationship("PositionUpdate", back_populates="trade")


class PositionUpdate(Base):
    """Track position changes over time"""
    __tablename__ = "position_updates"
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, server_default=func.now())
    
    trade_id = Column(Integer, ForeignKey("trades.id"), nullable=False)
    
    # Position snapshot
    current_price = Column(Numeric(10, 2))
    bid_price = Column(Numeric(10, 2))
    ask_price = Column(Numeric(10, 2))
    
    # P&L at this moment
    unrealized_pnl = Column(Numeric(10, 2))
    unrealized_pnl_percent = Column(Float)
    
    # Greeks snapshot (for options)
    delta = Column(Float)
    gamma = Column(Float)
    theta = Column(Float)
    vega = Column(Float)
    
    # Volume and OI
    volume = Column(Integer)
    open_interest = Column(Integer)
    
    # Relationship
    trade = relationship("Trade", back_populates="position_updates")
    
    # Index for time-series queries
    __table_args__ = (
        Index("idx_position_trade_time", "trade_id", "timestamp"),
    )


class MarketSnapshot(Base):
    """Point-in-time market conditions for analysis"""
    __tablename__ = "market_snapshots"
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, server_default=func.now())
    
    # Market indices
    spy_price = Column(Numeric(10, 2))
    qqq_price = Column(Numeric(10, 2))
    iwm_price = Column(Numeric(10, 2))
    vix_level = Column(Float)
    
    # Market internals
    advance_decline_ratio = Column(Float)
    put_call_ratio = Column(Float)
    high_low_ratio = Column(Float)
    
    # Breadth indicators
    stocks_above_ma50 = Column(Float)  # Percentage
    stocks_above_ma200 = Column(Float)
    
    # Volume metrics
    total_volume = Column(Integer)
    up_volume = Column(Integer)
    down_volume = Column(Integer)
    
    # Sentiment indicators
    fear_greed_index = Column(Float)
    market_sentiment_score = Column(Float)
    
    # Economic data
    ten_year_yield = Column(Float)
    dollar_index = Column(Float)
    gold_price = Column(Numeric(10, 2))
    oil_price = Column(Numeric(10, 2))
    
    __table_args__ = (
        Index("idx_market_timestamp", "timestamp"),
    )


class StrategyPerformance(Base):
    """Track performance metrics for each strategy"""
    __tablename__ = "strategy_performance"
    
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, nullable=False)
    strategy_name = Column(String(50), nullable=False)
    
    # Daily metrics
    total_trades = Column(Integer, default=0)
    winning_trades = Column(Integer, default=0)
    losing_trades = Column(Integer, default=0)
    
    # P&L metrics
    gross_pnl = Column(Numeric(10, 2))
    net_pnl = Column(Numeric(10, 2))
    total_commission = Column(Numeric(10, 2))
    
    # Risk metrics
    max_drawdown = Column(Numeric(10, 2))
    sharpe_ratio = Column(Float)
    win_rate = Column(Float)
    profit_factor = Column(Float)
    
    # Average metrics
    avg_win = Column(Numeric(10, 2))
    avg_loss = Column(Numeric(10, 2))
    avg_holding_period = Column(Float)  # hours
    
    # Best/worst trades
    best_trade_pnl = Column(Numeric(10, 2))
    worst_trade_pnl = Column(Numeric(10, 2))
    
    __table_args__ = (
        UniqueConstraint("date", "strategy_name"),
        Index("idx_strategy_perf", "strategy_name", "date"),
    )


class DecisionLog(Base):
    """Detailed log of all trading decisions"""
    __tablename__ = "decision_logs"
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, server_default=func.now())
    
    # Decision context
    symbol = Column(String(10))
    action = Column(String(20))  # ANALYZE, BUY, SELL, HOLD, SKIP
    
    # Input data
    market_data = Column(JSON)
    technical_indicators = Column(JSON)
    sentiment_data = Column(JSON)
    options_data = Column(JSON)
    
    # Decision process
    strategies_evaluated = Column(JSON)
    signals_generated = Column(JSON)
    risk_assessment = Column(JSON)
    
    # Claude's analysis
    claude_input = Column(Text)
    claude_response = Column(Text)
    claude_decision = Column(JSON)
    
    # Final decision
    decision_made = Column(String(50))
    decision_reasoning = Column(Text)
    confidence_score = Column(Float)
    
    # Execution details
    executed = Column(Boolean, default=False)
    execution_error = Column(Text)
    trade_id = Column(Integer, ForeignKey("trades.id"))
    
    __table_args__ = (
        Index("idx_decision_symbol_time", "symbol", "timestamp"),
    )


class Alert(Base):
    """System alerts and notifications"""
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, server_default=func.now())
    
    alert_type = Column(String(50))  # RISK, OPPORTUNITY, ERROR, INFO
    severity = Column(String(20))  # LOW, MEDIUM, HIGH, CRITICAL
    
    title = Column(String(200))
    message = Column(Text)
    
    # Context
    symbol = Column(String(10))
    trade_id = Column(Integer, ForeignKey("trades.id"))
    
    # Status
    acknowledged = Column(Boolean, default=False)
    acknowledged_at = Column(DateTime)
    resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime)
    
    # Additional data
    alert_metadata = Column(JSON)
    
    __table_args__ = (
        Index("idx_alert_type_severity", "alert_type", "severity"),
        Index("idx_alert_unresolved", "resolved", "severity"),
    )