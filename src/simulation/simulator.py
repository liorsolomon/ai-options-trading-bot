"""
Fully simulated trading environment for testing anytime
"""

import random
import asyncio
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import uuid
from loguru import logger


@dataclass
class SimulatedPosition:
    """Represents a position in the simulator"""
    symbol: str
    quantity: int
    entry_price: float
    current_price: float
    position_type: str = "stock"  # stock or option
    strike: Optional[float] = None
    expiration: Optional[datetime] = None
    option_type: Optional[str] = None  # CALL or PUT
    
    @property
    def market_value(self) -> float:
        return self.quantity * self.current_price
    
    @property
    def unrealized_pnl(self) -> float:
        return (self.current_price - self.entry_price) * self.quantity
    
    @property
    def unrealized_pnl_percent(self) -> float:
        if self.entry_price == 0:
            return 0
        return (self.unrealized_pnl / (self.entry_price * abs(self.quantity))) * 100


@dataclass
class SimulatedOrder:
    """Represents an order in the simulator"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    symbol: str = ""
    quantity: int = 0
    side: str = ""  # BUY or SELL
    order_type: str = ""  # MARKET or LIMIT
    limit_price: Optional[float] = None
    status: str = "PENDING"
    filled_price: Optional[float] = None
    filled_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    
    # Options specific
    is_option: bool = False
    strike: Optional[float] = None
    expiration: Optional[datetime] = None
    option_type: Optional[str] = None  # CALL or PUT


class TradingSimulator:
    """
    Fully simulated trading environment
    Works anytime, no market hours restrictions
    """
    
    def __init__(self, initial_cash: float = 100000.0):
        self.cash = initial_cash
        self.initial_cash = initial_cash
        self.positions: Dict[str, SimulatedPosition] = {}
        self.orders: List[SimulatedOrder] = []
        self.order_history: List[SimulatedOrder] = []
        
        # Simulated market data
        self.market_prices = {
            "SPY": 450.00,
            "QQQ": 380.00,
            "IWM": 200.00,
            "AAPL": 180.00,
            "MSFT": 420.00,
            "NVDA": 850.00,
            "TSLA": 250.00
        }
        
        # Volatility for price simulation
        self.volatility = {
            "SPY": 0.01,   # 1% daily volatility
            "QQQ": 0.015,
            "IWM": 0.02,
            "AAPL": 0.025,
            "MSFT": 0.02,
            "NVDA": 0.04,
            "TSLA": 0.05
        }
        
        logger.info(f"Trading Simulator initialized with ${initial_cash:,.2f}")
    
    def get_market_price(self, symbol: str) -> float:
        """Get simulated market price with random movement"""
        if symbol not in self.market_prices:
            # Add new symbol with random price
            self.market_prices[symbol] = random.uniform(10, 500)
            self.volatility[symbol] = 0.02
        
        # Simulate price movement
        current_price = self.market_prices[symbol]
        volatility = self.volatility.get(symbol, 0.02)
        
        # Random walk with slight upward bias
        change = random.gauss(0.0001, volatility)  # Slight positive drift
        new_price = current_price * (1 + change)
        
        # Update stored price
        self.market_prices[symbol] = new_price
        
        return round(new_price, 2)
    
    def get_simulated_price(self, symbol: str) -> float:
        """Alias for get_market_price for compatibility"""
        return self.get_market_price(symbol)
    
    def get_portfolio_value(self) -> float:
        """Get total portfolio value (cash + positions)"""
        positions_value = sum(p.market_value for p in self.positions.values())
        return self.cash + positions_value
    
    def get_positions(self) -> Dict[str, Any]:
        """Get current positions as dict"""
        return {
            symbol: {
                "quantity": pos.quantity,
                "entry_price": pos.entry_price,
                "current_price": pos.current_price,
                "pnl": pos.unrealized_pnl,
                "value": pos.market_value
            }
            for symbol, pos in self.positions.items()
        }
    
    def get_option_price(self, underlying: str, strike: float, option_type: str, 
                        days_to_expiry: int) -> float:
        """Simple option pricing simulation"""
        underlying_price = self.get_market_price(underlying)
        
        # Intrinsic value
        if option_type == "CALL":
            intrinsic = max(0, underlying_price - strike)
        else:  # PUT
            intrinsic = max(0, strike - underlying_price)
        
        # Time value (simplified)
        time_value = (days_to_expiry / 365) * underlying_price * 0.2 * self.volatility.get(underlying, 0.02)
        
        # Option price
        option_price = intrinsic + time_value
        
        return round(max(0.01, option_price), 2)
    
    async def place_order(self, symbol: str, quantity: int, side: str, 
                         order_type: str = "MARKET", limit_price: Optional[float] = None,
                         is_option: bool = False, strike: Optional[float] = None,
                         expiration: Optional[datetime] = None, 
                         option_type: Optional[str] = None) -> SimulatedOrder:
        """Place a simulated order"""
        
        order = SimulatedOrder(
            symbol=symbol,
            quantity=quantity,
            side=side,
            order_type=order_type,
            limit_price=limit_price,
            is_option=is_option,
            strike=strike,
            expiration=expiration,
            option_type=option_type
        )
        
        self.orders.append(order)
        
        # Simulate order execution
        if order_type == "MARKET":
            # Market orders execute immediately
            await self._execute_order(order)
        else:
            # Limit orders may or may not execute
            market_price = self.get_market_price(symbol)
            if side == "BUY" and limit_price >= market_price:
                await self._execute_order(order)
            elif side == "SELL" and limit_price <= market_price:
                await self._execute_order(order)
            else:
                order.status = "PENDING"
                logger.info(f"Limit order placed: {side} {quantity} {symbol} @ ${limit_price}")
        
        return order
    
    async def _execute_order(self, order: SimulatedOrder):
        """Execute a simulated order"""
        
        # Get execution price
        if order.is_option:
            days_to_expiry = (order.expiration - datetime.now()).days if order.expiration else 30
            exec_price = self.get_option_price(
                order.symbol, order.strike, order.option_type, days_to_expiry
            )
        else:
            exec_price = self.get_market_price(order.symbol)
        
        # Check if we have enough cash for buy orders
        total_cost = exec_price * order.quantity
        
        if order.side == "BUY":
            if total_cost > self.cash:
                order.status = "REJECTED"
                logger.warning(f"Order rejected: Insufficient funds (need ${total_cost:.2f}, have ${self.cash:.2f})")
                return
            
            # Execute buy
            self.cash -= total_cost
            
            # Add or update position
            position_key = f"{order.symbol}_{order.strike}_{order.option_type}" if order.is_option else order.symbol
            
            if position_key in self.positions:
                # Update existing position (average in)
                pos = self.positions[position_key]
                total_qty = pos.quantity + order.quantity
                avg_price = ((pos.entry_price * pos.quantity) + (exec_price * order.quantity)) / total_qty
                pos.quantity = total_qty
                pos.entry_price = avg_price
                pos.current_price = exec_price
            else:
                # Create new position
                self.positions[position_key] = SimulatedPosition(
                    symbol=order.symbol,
                    quantity=order.quantity,
                    entry_price=exec_price,
                    current_price=exec_price,
                    position_type="option" if order.is_option else "stock",
                    strike=order.strike,
                    expiration=order.expiration,
                    option_type=order.option_type
                )
            
        else:  # SELL
            position_key = f"{order.symbol}_{order.strike}_{order.option_type}" if order.is_option else order.symbol
            
            if position_key not in self.positions:
                order.status = "REJECTED"
                logger.warning(f"Order rejected: No position to sell")
                return
            
            pos = self.positions[position_key]
            if pos.quantity < order.quantity:
                order.status = "REJECTED"
                logger.warning(f"Order rejected: Insufficient position (have {pos.quantity}, selling {order.quantity})")
                return
            
            # Execute sell
            self.cash += total_cost
            pos.quantity -= order.quantity
            
            if pos.quantity == 0:
                del self.positions[position_key]
        
        # Update order
        order.status = "FILLED"
        order.filled_price = exec_price
        order.filled_at = datetime.now()
        
        # Add to history
        self.order_history.append(order)
        
        logger.info(f"Order executed: {order.side} {order.quantity} {order.symbol} @ ${exec_price:.2f}")
    
    def get_account_value(self) -> float:
        """Get total account value"""
        positions_value = sum(pos.market_value for pos in self.positions.values())
        return self.cash + positions_value
    
    def get_pnl(self) -> float:
        """Get total P&L"""
        return self.get_account_value() - self.initial_cash
    
    def get_pnl_percent(self) -> float:
        """Get P&L percentage"""
        return (self.get_pnl() / self.initial_cash) * 100
    
    def update_prices(self):
        """Update all position prices (simulate market movement)"""
        for pos in self.positions.values():
            if pos.position_type == "option":
                days_to_expiry = (pos.expiration - datetime.now()).days if pos.expiration else 30
                pos.current_price = self.get_option_price(
                    pos.symbol, pos.strike, pos.option_type, days_to_expiry
                )
            else:
                pos.current_price = self.get_market_price(pos.symbol)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get account summary"""
        self.update_prices()
        
        return {
            "cash": round(self.cash, 2),
            "positions_value": round(sum(pos.market_value for pos in self.positions.values()), 2),
            "total_value": round(self.get_account_value(), 2),
            "initial_value": round(self.initial_cash, 2),
            "total_pnl": round(self.get_pnl(), 2),
            "total_pnl_percent": round(self.get_pnl_percent(), 2),
            "num_positions": len(self.positions),
            "num_orders": len(self.order_history)
        }
    
    def reset(self):
        """Reset simulator to initial state"""
        self.cash = self.initial_cash
        self.positions.clear()
        self.orders.clear()
        self.order_history.clear()
        logger.info("Simulator reset to initial state")