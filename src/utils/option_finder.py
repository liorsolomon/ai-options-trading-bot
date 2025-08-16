"""
Utility to find available option contracts on Alpaca
"""

import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from loguru import logger


class OptionFinder:
    """Find available option contracts that can be traded"""
    
    @staticmethod
    def get_standard_monthly_expiration(months_ahead: int = 0) -> datetime:
        """
        Get standard monthly option expiration (3rd Friday of month)
        
        Args:
            months_ahead: Number of months ahead (0 = current month)
            
        Returns:
            datetime: The expiration date
        """
        today = datetime.now()
        
        # Calculate target month/year
        target_month = today.month + months_ahead
        target_year = today.year
        
        while target_month > 12:
            target_month -= 12
            target_year += 1
            
        # Find third Friday of target month
        first_day = datetime(target_year, target_month, 1)
        
        # Find first Friday
        days_until_friday = (4 - first_day.weekday()) % 7
        if days_until_friday == 0:
            days_until_friday = 7
        first_friday = first_day + timedelta(days=days_until_friday)
        
        # Third Friday is 14 days after first Friday
        third_friday = first_friday + timedelta(days=14)
        
        return third_friday
    
    @staticmethod
    def get_weekly_expiration(weeks_ahead: int = 1) -> datetime:
        """
        Get weekly option expiration (Friday)
        
        Args:
            weeks_ahead: Number of weeks ahead
            
        Returns:
            datetime: The expiration date
        """
        today = datetime.now()
        
        # Find next Friday
        days_until_friday = (4 - today.weekday()) % 7
        if days_until_friday == 0:
            days_until_friday = 7
            
        next_friday = today + timedelta(days=days_until_friday)
        
        # Add weeks if requested
        target_friday = next_friday + timedelta(weeks=weeks_ahead - 1)
        
        return target_friday
    
    @staticmethod
    def format_option_symbol(
        ticker: str,
        expiration: datetime,
        option_type: str,
        strike: float
    ) -> str:
        """
        Format option symbol in OCC format
        
        Args:
            ticker: Stock ticker
            expiration: Expiration date
            option_type: "CALL" or "PUT"
            strike: Strike price
            
        Returns:
            str: Formatted option symbol (e.g., SPY241220C00440000)
        """
        # Format: TICKER + YYMMDD + C/P + STRIKE*1000 (8 digits)
        exp_str = expiration.strftime("%y%m%d")
        opt_type = "C" if option_type.upper() == "CALL" else "P"
        strike_str = f"{int(strike * 1000):08d}"
        
        symbol = f"{ticker}{exp_str}{opt_type}{strike_str}"
        
        logger.debug(f"Formatted option symbol: {symbol}")
        return symbol
    
    @staticmethod
    def get_common_strikes(current_price: float, num_strikes: int = 5) -> List[float]:
        """
        Get common strike prices around current price
        
        Args:
            current_price: Current stock price
            num_strikes: Number of strikes above and below
            
        Returns:
            List[float]: List of strike prices
        """
        # Round to nearest $5 for stocks over $100, $1 for under
        if current_price > 100:
            interval = 5
            base = round(current_price / 5) * 5
        else:
            interval = 1
            base = round(current_price)
            
        strikes = []
        for i in range(-num_strikes, num_strikes + 1):
            strike = base + (i * interval)
            if strike > 0:  # Only positive strikes
                strikes.append(float(strike))
                
        return strikes
    
    @staticmethod
    def get_spy_weekly_options(weeks_ahead: int = 1) -> List[Dict]:
        """
        Get common SPY weekly option contracts
        
        Args:
            weeks_ahead: Number of weeks ahead
            
        Returns:
            List[Dict]: List of option contract details
        """
        # SPY typically trades around 550-560
        current_spy = 555.0  # Approximate
        
        expiration = OptionFinder.get_weekly_expiration(weeks_ahead)
        strikes = OptionFinder.get_common_strikes(current_spy, num_strikes=3)
        
        options = []
        for strike in strikes:
            for opt_type in ["CALL", "PUT"]:
                symbol = OptionFinder.format_option_symbol(
                    "SPY", expiration, opt_type, strike
                )
                options.append({
                    "symbol": symbol,
                    "ticker": "SPY",
                    "strike": strike,
                    "type": opt_type,
                    "expiration": expiration.strftime("%Y-%m-%d"),
                    "days_to_expiry": (expiration - datetime.now()).days
                })
                
        return options
    
    @staticmethod
    def get_safe_test_option() -> Dict:
        """
        Get a safe option for testing (SPY weekly ATM)
        
        Returns:
            Dict: Option contract details
        """
        # Use SPY weekly, 1 week out, at-the-money
        expiration = OptionFinder.get_weekly_expiration(1)
        
        # Use round strike near current SPY price
        strike = 555.0  # Typical SPY level
        
        symbol = OptionFinder.format_option_symbol(
            "SPY", expiration, "CALL", strike
        )
        
        return {
            "symbol": symbol,
            "ticker": "SPY",
            "strike": strike,
            "type": "CALL",
            "expiration": expiration.strftime("%Y-%m-%d"),
            "days_to_expiry": (expiration - datetime.now()).days,
            "description": f"SPY ${strike} Call expiring {expiration.strftime('%b %d')}"
        }


if __name__ == "__main__":
    # Test the option finder
    finder = OptionFinder()
    
    print("Testing Option Finder")
    print("=" * 50)
    
    # Get safe test option
    test_option = finder.get_safe_test_option()
    print(f"\nSafe Test Option:")
    print(f"  Symbol: {test_option['symbol']}")
    print(f"  Description: {test_option['description']}")
    
    # Get SPY weekly options
    print(f"\nSPY Weekly Options (1 week out):")
    options = finder.get_spy_weekly_options(1)
    for opt in options[:6]:  # Show first 6
        print(f"  {opt['symbol']} - {opt['ticker']} ${opt['strike']} {opt['type']}")
    
    # Test monthly expiration
    monthly = finder.get_standard_monthly_expiration(0)
    print(f"\nThis month's expiration: {monthly.strftime('%Y-%m-%d')}")
    
    next_monthly = finder.get_standard_monthly_expiration(1)
    print(f"Next month's expiration: {next_monthly.strftime('%Y-%m-%d')}")