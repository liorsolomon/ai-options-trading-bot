"""
Trading Bot Monitoring and Alerting System
Tracks performance, errors, and sends notifications
"""

import json
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path
from loguru import logger
import pandas as pd


@dataclass
class PerformanceMetrics:
    """Performance tracking metrics"""
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    total_pnl: float
    average_win: float
    average_loss: float
    sharpe_ratio: float
    max_drawdown: float
    current_streak: int  # Positive for wins, negative for losses
    best_trade: Dict[str, Any]
    worst_trade: Dict[str, Any]
    active_positions: int
    portfolio_value: float


@dataclass
class SystemHealth:
    """System health status"""
    api_status: Dict[str, bool]  # API name -> status
    database_connected: bool
    last_execution: datetime
    errors_last_hour: int
    warnings_last_hour: int
    cpu_usage: float
    memory_usage: float
    disk_usage: float


@dataclass
class Alert:
    """System alert"""
    level: str  # INFO, WARNING, ERROR, CRITICAL
    category: str  # PERFORMANCE, SYSTEM, TRADING, RISK
    message: str
    timestamp: datetime
    details: Dict[str, Any]
    action_required: bool


class TradingMonitor:
    """Main monitoring system for the trading bot"""
    
    def __init__(self, alert_webhook: Optional[str] = None):
        self.alert_webhook = alert_webhook
        self.metrics_history = []
        self.alerts = []
        self.performance_thresholds = {
            "min_win_rate": 0.40,  # Alert if win rate drops below 40%
            "max_drawdown": 0.20,  # Alert if drawdown exceeds 20%
            "max_loss_streak": 5,  # Alert after 5 consecutive losses
            "min_sharpe": 0.5,  # Alert if Sharpe ratio drops below 0.5
        }
        self.monitoring_dir = Path(__file__).parent.parent.parent / "monitoring_data"
        self.monitoring_dir.mkdir(exist_ok=True)
        
    async def track_trade(self, trade: Dict[str, Any]) -> None:
        """Track a completed trade"""
        
        # Update metrics
        metrics = await self.calculate_metrics()
        
        # Check for alerts
        alerts = self._check_performance_alerts(metrics, trade)
        
        for alert in alerts:
            await self.send_alert(alert)
            
        # Log trade
        logger.info(f"Trade tracked: {trade.get('ticker')} - P&L: ${trade.get('pnl', 0):.2f}")
        
    async def calculate_metrics(self) -> PerformanceMetrics:
        """Calculate current performance metrics"""
        
        # This would normally query the database
        # For now, using mock data
        trades = self._get_recent_trades()
        
        if not trades:
            return PerformanceMetrics(
                total_trades=0,
                winning_trades=0,
                losing_trades=0,
                win_rate=0.0,
                total_pnl=0.0,
                average_win=0.0,
                average_loss=0.0,
                sharpe_ratio=0.0,
                max_drawdown=0.0,
                current_streak=0,
                best_trade={},
                worst_trade={},
                active_positions=0,
                portfolio_value=100000.0
            )
        
        winning = [t for t in trades if t["pnl"] > 0]
        losing = [t for t in trades if t["pnl"] < 0]
        
        metrics = PerformanceMetrics(
            total_trades=len(trades),
            winning_trades=len(winning),
            losing_trades=len(losing),
            win_rate=len(winning) / len(trades) if trades else 0,
            total_pnl=sum(t["pnl"] for t in trades),
            average_win=sum(t["pnl"] for t in winning) / len(winning) if winning else 0,
            average_loss=sum(t["pnl"] for t in losing) / len(losing) if losing else 0,
            sharpe_ratio=self._calculate_sharpe_ratio(trades),
            max_drawdown=self._calculate_max_drawdown(trades),
            current_streak=self._calculate_streak(trades),
            best_trade=max(trades, key=lambda x: x["pnl"]) if trades else {},
            worst_trade=min(trades, key=lambda x: x["pnl"]) if trades else {},
            active_positions=self._count_active_positions(),
            portfolio_value=self._get_portfolio_value()
        )
        
        self.metrics_history.append({
            "timestamp": datetime.now(),
            "metrics": asdict(metrics)
        })
        
        return metrics
        
    def _calculate_sharpe_ratio(self, trades: List[Dict]) -> float:
        """Calculate Sharpe ratio"""
        if not trades:
            return 0.0
            
        returns = [t["pnl"] / 100000 for t in trades]  # Assuming $100k portfolio
        
        if len(returns) < 2:
            return 0.0
            
        avg_return = sum(returns) / len(returns)
        std_return = pd.Series(returns).std()
        
        if std_return == 0:
            return 0.0
            
        # Annualized Sharpe (assuming daily trades, 252 trading days)
        return (avg_return * 252) / (std_return * (252 ** 0.5))
        
    def _calculate_max_drawdown(self, trades: List[Dict]) -> float:
        """Calculate maximum drawdown"""
        if not trades:
            return 0.0
            
        cumulative = []
        total = 0
        
        for trade in trades:
            total += trade["pnl"]
            cumulative.append(total)
            
        peak = cumulative[0]
        max_dd = 0
        
        for value in cumulative:
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak if peak > 0 else 0
            max_dd = max(max_dd, drawdown)
            
        return max_dd
        
    def _calculate_streak(self, trades: List[Dict]) -> int:
        """Calculate current win/loss streak"""
        if not trades:
            return 0
            
        streak = 0
        last_sign = None
        
        for trade in reversed(trades):  # Start from most recent
            sign = 1 if trade["pnl"] > 0 else -1
            
            if last_sign is None:
                last_sign = sign
                streak = sign
            elif sign == last_sign:
                streak += sign
            else:
                break
                
        return streak
        
    def _get_recent_trades(self) -> List[Dict]:
        """Get recent trades from database"""
        # Mock data for testing
        return [
            {"ticker": "AAPL", "pnl": 250, "timestamp": datetime.now() - timedelta(hours=1)},
            {"ticker": "SPY", "pnl": -100, "timestamp": datetime.now() - timedelta(hours=2)},
            {"ticker": "TSLA", "pnl": 500, "timestamp": datetime.now() - timedelta(hours=3)},
        ]
        
    def _count_active_positions(self) -> int:
        """Count active positions"""
        # Would query database
        return 3
        
    def _get_portfolio_value(self) -> float:
        """Get current portfolio value"""
        # Would query broker API
        return 102500.0
        
    def _check_performance_alerts(
        self,
        metrics: PerformanceMetrics,
        latest_trade: Dict
    ) -> List[Alert]:
        """Check for performance-based alerts"""
        
        alerts = []
        
        # Win rate alert
        if metrics.win_rate < self.performance_thresholds["min_win_rate"]:
            alerts.append(Alert(
                level="WARNING",
                category="PERFORMANCE",
                message=f"Win rate dropped to {metrics.win_rate:.1%}",
                timestamp=datetime.now(),
                details={"win_rate": metrics.win_rate, "threshold": self.performance_thresholds["min_win_rate"]},
                action_required=True
            ))
            
        # Drawdown alert
        if metrics.max_drawdown > self.performance_thresholds["max_drawdown"]:
            alerts.append(Alert(
                level="CRITICAL",
                category="RISK",
                message=f"Maximum drawdown exceeded: {metrics.max_drawdown:.1%}",
                timestamp=datetime.now(),
                details={"drawdown": metrics.max_drawdown, "threshold": self.performance_thresholds["max_drawdown"]},
                action_required=True
            ))
            
        # Losing streak alert
        if metrics.current_streak <= -self.performance_thresholds["max_loss_streak"]:
            alerts.append(Alert(
                level="WARNING",
                category="PERFORMANCE",
                message=f"Losing streak: {abs(metrics.current_streak)} consecutive losses",
                timestamp=datetime.now(),
                details={"streak": metrics.current_streak},
                action_required=True
            ))
            
        # Sharpe ratio alert
        if metrics.sharpe_ratio < self.performance_thresholds["min_sharpe"]:
            alerts.append(Alert(
                level="INFO",
                category="PERFORMANCE",
                message=f"Sharpe ratio below target: {metrics.sharpe_ratio:.2f}",
                timestamp=datetime.now(),
                details={"sharpe": metrics.sharpe_ratio, "threshold": self.performance_thresholds["min_sharpe"]},
                action_required=False
            ))
            
        return alerts
        
    async def check_system_health(self) -> SystemHealth:
        """Check overall system health"""
        
        health = SystemHealth(
            api_status={
                "alpaca": await self._check_alpaca_api(),
                "supabase": await self._check_database(),
                "anthropic": await self._check_claude_api()
            },
            database_connected=await self._check_database(),
            last_execution=datetime.now(),
            errors_last_hour=self._count_recent_errors(),
            warnings_last_hour=self._count_recent_warnings(),
            cpu_usage=self._get_cpu_usage(),
            memory_usage=self._get_memory_usage(),
            disk_usage=self._get_disk_usage()
        )
        
        # Check for system alerts
        if health.errors_last_hour > 10:
            await self.send_alert(Alert(
                level="ERROR",
                category="SYSTEM",
                message=f"High error rate: {health.errors_last_hour} errors in last hour",
                timestamp=datetime.now(),
                details={"error_count": health.errors_last_hour},
                action_required=True
            ))
            
        if health.memory_usage > 0.9:
            await self.send_alert(Alert(
                level="WARNING",
                category="SYSTEM",
                message=f"High memory usage: {health.memory_usage:.1%}",
                timestamp=datetime.now(),
                details={"memory": health.memory_usage},
                action_required=True
            ))
            
        return health
        
    async def _check_alpaca_api(self) -> bool:
        """Check Alpaca API status"""
        # Would make actual API call
        return True
        
    async def _check_database(self) -> bool:
        """Check database connectivity"""
        # Would test database connection
        return True
        
    async def _check_claude_api(self) -> bool:
        """Check Claude API status"""
        # Would test API key
        return True
        
    def _count_recent_errors(self) -> int:
        """Count errors in last hour"""
        # Would parse log files
        return 2
        
    def _count_recent_warnings(self) -> int:
        """Count warnings in last hour"""
        # Would parse log files
        return 5
        
    def _get_cpu_usage(self) -> float:
        """Get CPU usage percentage"""
        try:
            import psutil
            return psutil.cpu_percent() / 100
        except:
            return 0.3  # Mock value
            
    def _get_memory_usage(self) -> float:
        """Get memory usage percentage"""
        try:
            import psutil
            return psutil.virtual_memory().percent / 100
        except:
            return 0.5  # Mock value
            
    def _get_disk_usage(self) -> float:
        """Get disk usage percentage"""
        try:
            import psutil
            return psutil.disk_usage('/').percent / 100
        except:
            return 0.4  # Mock value
            
    async def send_alert(self, alert) -> None:
        """Send alert via configured channels"""
        
        # Handle dict or Alert object
        if isinstance(alert, dict):
            alert = Alert(
                level=alert.get("level", "INFO"),
                category=alert.get("category", "SYSTEM"),
                message=alert.get("message", ""),
                timestamp=alert.get("timestamp", datetime.now()),
                details=alert.get("details", {}),
                action_required=alert.get("action_required", False)
            )
        
        # Log alert
        log_message = f"[{alert.level}] {alert.category}: {alert.message}"
        
        if alert.level == "CRITICAL":
            logger.critical(log_message)
        elif alert.level == "ERROR":
            logger.error(log_message)
        elif alert.level == "WARNING":
            logger.warning(log_message)
        else:
            logger.info(log_message)
            
        # Store alert
        self.alerts.append(alert)
        
        # Send to webhook if configured
        if self.alert_webhook and alert.level in ["CRITICAL", "ERROR"]:
            await self._send_webhook_alert(alert)
            
    async def _send_webhook_alert(self, alert: Alert) -> None:
        """Send alert to webhook"""
        # Would send to Slack/Discord/etc
        pass
        
    def generate_report(self) -> str:
        """Generate monitoring report"""
        
        if not self.metrics_history:
            return "No metrics available yet"
            
        latest = self.metrics_history[-1]["metrics"]
        
        report = f"""
📊 TRADING BOT MONITORING REPORT
{'='*50}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📈 PERFORMANCE METRICS
----------------------
Total Trades: {latest['total_trades']}
Win Rate: {latest['win_rate']:.1%}
Total P&L: ${latest['total_pnl']:.2f}
Sharpe Ratio: {latest['sharpe_ratio']:.2f}
Max Drawdown: {latest['max_drawdown']:.1%}
Current Streak: {latest['current_streak']} {'wins' if latest['current_streak'] > 0 else 'losses'}

💰 PORTFOLIO STATUS
-------------------
Portfolio Value: ${latest['portfolio_value']:,.2f}
Active Positions: {latest['active_positions']}
Average Win: ${latest['average_win']:.2f}
Average Loss: ${latest['average_loss']:.2f}

🚨 RECENT ALERTS
----------------"""
        
        recent_alerts = self.alerts[-5:] if self.alerts else []
        for alert in recent_alerts:
            report += f"\n[{alert.level}] {alert.message} ({alert.timestamp.strftime('%H:%M')})"
            
        if not recent_alerts:
            report += "\nNo recent alerts"
            
        return report
        
    async def save_metrics(self) -> None:
        """Save metrics to file"""
        
        metrics_file = self.monitoring_dir / f"metrics_{datetime.now().strftime('%Y%m%d')}.json"
        
        with open(metrics_file, 'w') as f:
            json.dump(self.metrics_history, f, indent=2, default=str)
            
        logger.info(f"Metrics saved to {metrics_file}")


# Example usage
async def test_monitor():
    """Test the monitoring system"""
    
    monitor = TradingMonitor()
    
    # Track a trade
    await monitor.track_trade({
        "ticker": "AAPL",
        "pnl": 250,
        "type": "CALL",
        "entry": 175,
        "exit": 177.5
    })
    
    # Check system health
    health = await monitor.check_system_health()
    
    # Calculate metrics
    metrics = await monitor.calculate_metrics()
    
    # Generate report
    report = monitor.generate_report()
    print(report)
    
    # Save metrics
    await monitor.save_metrics()
    
    print("\n✅ Monitoring system operational!")


if __name__ == "__main__":
    asyncio.run(test_monitor())