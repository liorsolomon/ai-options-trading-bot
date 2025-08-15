"""
Alpaca Trading API client for options trading
"""

import os
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from decimal import Decimal

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import (
    MarketOrderRequest,
    LimitOrderRequest,
    GetOrdersRequest
)
from alpaca.trading.enums import (
    OrderSide,
    TimeInForce,
    OrderType,
    OrderStatus,
    AssetClass
)
from alpaca.data.historical import StockHistoricalDataClient, OptionHistoricalDataClient
from alpaca.data.requests import (
    StockBarsRequest,
    OptionChainRequest,
    OptionBarsRequest,
    StockLatestQuoteRequest
)
from alpaca.data.timeframe import TimeFrame
from loguru import logger


class AlpacaOptionsClient:
    """
    Alpaca Trading API client specialized for options trading
    """
    
    def __init__(self):
        api_key = os.getenv("ALPACA_API_KEY")
        secret_key = os.getenv("ALPACA_SECRET_KEY")
        
        if not api_key or not secret_key:
            raise ValueError("Alpaca API credentials not found in environment")
        
        # Initialize trading client for orders and positions
        self.trading_client = TradingClient(
            api_key=api_key,
            secret_key=secret_key,
            paper=os.getenv("TRADING_MODE", "paper") == "paper"
        )
        
        # Initialize data clients for market data
        self.stock_data_client = StockHistoricalDataClient(api_key, secret_key)
        self.option_data_client = OptionHistoricalDataClient(api_key, secret_key)
        
        self.connected = False
        logger.info(f"Alpaca client initialized in {os.getenv('TRADING_MODE', 'paper')} mode")
    
    async def connect(self) -> bool:
        """Connect to Alpaca API and verify credentials"""
        try:
            # Test connection by getting account info
            account = self.trading_client.get_account()
            if account:
                self.connected = True
                logger.info(f"Connected to Alpaca - Account: {account.account_number}")
                logger.info(f"Buying Power: ${account.buying_power}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to connect to Alpaca: {e}")
            return False
    
    async def get_account_info(self) -> Dict[str, Any]:
        """Get account information including buying power and positions"""
        try:
            account = self.trading_client.get_account()
            return {
                "buying_power": float(account.buying_power),
                "cash": float(account.cash),
                "portfolio_value": float(account.portfolio_value),
                "day_trading_buying_power": float(account.daytrading_buying_power),
                "pattern_day_trader": account.pattern_day_trader,
                "trading_blocked": account.trading_blocked,
                "options_approved_level": account.options_approved_level,
                "options_trading_level": account.options_trading_level
            }
        except Exception as e:
            logger.error(f"Error getting account info: {e}")
            raise
    
    async def get_option_chain(self, symbol: str, expiration_date: Optional[datetime] = None) -> List[Dict]:
        """Get option chain for a symbol"""
        try:
            # If no expiration date provided, get next monthly expiration
            if not expiration_date:
                expiration_date = self._get_next_monthly_expiration()
            
            request = OptionChainRequest(
                underlying_symbol=symbol,
                expiration_date_gte=expiration_date.date(),
                expiration_date_lte=(expiration_date + timedelta(days=7)).date()
            )
            
            chain = self.option_data_client.get_option_chain(request)
            
            options_list = []
            for option in chain:
                options_list.append({
                    "symbol": option.symbol,
                    "underlying": option.underlying_symbol,
                    "strike": float(option.strike_price),
                    "expiration": option.expiration_date.isoformat(),
                    "type": option.option_type,  # CALL or PUT
                    "bid": float(option.latest_quote.bid_price) if option.latest_quote else None,
                    "ask": float(option.latest_quote.ask_price) if option.latest_quote else None,
                    "volume": option.volume,
                    "open_interest": option.open_interest,
                    "implied_volatility": float(option.implied_volatility) if option.implied_volatility else None,
                    "delta": float(option.greeks.delta) if option.greeks else None,
                    "gamma": float(option.greeks.gamma) if option.greeks else None,
                    "theta": float(option.greeks.theta) if option.greeks else None,
                    "vega": float(option.greeks.vega) if option.greeks else None
                })
            
            return options_list
            
        except Exception as e:
            logger.error(f"Error getting option chain for {symbol}: {e}")
            raise
    
    async def place_option_order(
        self,
        option_symbol: str,
        side: str,  # "buy" or "sell"
        quantity: int,
        order_type: str = "market",  # "market" or "limit"
        limit_price: Optional[float] = None,
        time_in_force: str = "day"  # "day", "gtc", "ioc", "fok"
    ) -> Dict[str, Any]:
        """Place an option order"""
        try:
            # Convert string parameters to enums
            order_side = OrderSide.BUY if side.lower() == "buy" else OrderSide.SELL
            tif = TimeInForce[time_in_force.upper()]
            
            if order_type.lower() == "market":
                request = MarketOrderRequest(
                    symbol=option_symbol,
                    qty=quantity,
                    side=order_side,
                    time_in_force=tif,
                    asset_class=AssetClass.US_OPTION
                )
            else:  # limit order
                if not limit_price:
                    raise ValueError("Limit price required for limit orders")
                
                request = LimitOrderRequest(
                    symbol=option_symbol,
                    qty=quantity,
                    side=order_side,
                    time_in_force=tif,
                    limit_price=limit_price,
                    asset_class=AssetClass.US_OPTION
                )
            
            order = self.trading_client.submit_order(request)
            
            logger.info(f"Option order placed: {order.id} - {side} {quantity} {option_symbol}")
            
            return {
                "order_id": order.id,
                "symbol": order.symbol,
                "quantity": order.qty,
                "side": order.side,
                "type": order.order_type,
                "status": order.status,
                "submitted_at": order.submitted_at.isoformat() if order.submitted_at else None,
                "filled_qty": order.filled_qty,
                "filled_avg_price": float(order.filled_avg_price) if order.filled_avg_price else None
            }
            
        except Exception as e:
            logger.error(f"Error placing option order: {e}")
            raise
    
    async def get_positions(self) -> List[Dict[str, Any]]:
        """Get all current positions"""
        try:
            positions = self.trading_client.get_all_positions()
            
            position_list = []
            for pos in positions:
                position_list.append({
                    "symbol": pos.symbol,
                    "quantity": int(pos.qty),
                    "avg_entry_price": float(pos.avg_entry_price),
                    "market_value": float(pos.market_value),
                    "cost_basis": float(pos.cost_basis),
                    "unrealized_pl": float(pos.unrealized_pl),
                    "unrealized_plpc": float(pos.unrealized_plpc),
                    "current_price": float(pos.current_price) if pos.current_price else None,
                    "asset_class": pos.asset_class
                })
            
            return position_list
            
        except Exception as e:
            logger.error(f"Error getting positions: {e}")
            raise
    
    async def get_orders(self, status: str = "open") -> List[Dict[str, Any]]:
        """Get orders by status"""
        try:
            request = GetOrdersRequest(
                status=OrderStatus[status.upper()] if status else None,
                limit=100
            )
            
            orders = self.trading_client.get_orders(request)
            
            order_list = []
            for order in orders:
                order_list.append({
                    "order_id": order.id,
                    "symbol": order.symbol,
                    "quantity": order.qty,
                    "side": order.side,
                    "type": order.order_type,
                    "status": order.status,
                    "limit_price": float(order.limit_price) if order.limit_price else None,
                    "filled_qty": order.filled_qty,
                    "filled_avg_price": float(order.filled_avg_price) if order.filled_avg_price else None,
                    "submitted_at": order.submitted_at.isoformat() if order.submitted_at else None
                })
            
            return order_list
            
        except Exception as e:
            logger.error(f"Error getting orders: {e}")
            raise
    
    async def cancel_order(self, order_id: str) -> bool:
        """Cancel an order"""
        try:
            self.trading_client.cancel_order_by_id(order_id)
            logger.info(f"Order {order_id} cancelled")
            return True
        except Exception as e:
            logger.error(f"Error cancelling order {order_id}: {e}")
            return False
    
    async def close_position(self, symbol: str, qty: Optional[int] = None) -> bool:
        """Close a position"""
        try:
            if qty:
                self.trading_client.close_position(symbol, qty=qty)
            else:
                self.trading_client.close_position(symbol)
            
            logger.info(f"Position closed: {symbol}")
            return True
        except Exception as e:
            logger.error(f"Error closing position {symbol}: {e}")
            return False
    
    async def get_stock_quote(self, symbol: str) -> Dict[str, float]:
        """Get latest stock quote"""
        try:
            request = StockLatestQuoteRequest(symbol_or_symbols=symbol)
            quote = self.stock_data_client.get_stock_latest_quote(request)
            
            if symbol in quote:
                q = quote[symbol]
                return {
                    "bid": float(q.bid_price),
                    "ask": float(q.ask_price),
                    "bid_size": q.bid_size,
                    "ask_size": q.ask_size,
                    "timestamp": q.timestamp.isoformat()
                }
            return {}
            
        except Exception as e:
            logger.error(f"Error getting quote for {symbol}: {e}")
            raise
    
    def _get_next_monthly_expiration(self) -> datetime:
        """Get next monthly option expiration (3rd Friday)"""
        today = datetime.now()
        
        # Start from next month
        if today.day >= 15:  # If past mid-month, go to next month
            if today.month == 12:
                year = today.year + 1
                month = 1
            else:
                year = today.year
                month = today.month + 1
        else:
            year = today.year
            month = today.month
        
        # Find third Friday
        first_day = datetime(year, month, 1)
        first_friday = first_day + timedelta(days=(4 - first_day.weekday()) % 7)
        third_friday = first_friday + timedelta(weeks=2)
        
        return third_friday