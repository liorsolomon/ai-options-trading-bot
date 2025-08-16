"""
Claude AI Decision Maker
Integrates with Claude API to make intelligent trading decisions
"""

import os
import json
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from loguru import logger
import anthropic


@dataclass
class TradingContext:
    """Context for trading decision"""
    timestamp: datetime
    ticker: str
    current_price: float
    market_conditions: Dict[str, Any]
    whatsapp_signals: List[Dict]
    news_sentiment: Dict[str, Any]
    technical_indicators: Dict[str, float]
    recent_performance: Dict[str, float]
    portfolio_state: Dict[str, Any]
    risk_metrics: Dict[str, float]


@dataclass 
class TradingDecision:
    """AI-generated trading decision"""
    action: str  # BUY_CALL, BUY_PUT, SELL, HOLD
    ticker: str
    option_type: Optional[str]
    strike_price: Optional[float]
    expiration_days: Optional[int]
    quantity: int
    confidence: float
    reasoning: str
    risk_assessment: str
    expected_outcome: str
    stop_loss: Optional[float]
    take_profit: Optional[float]


class ClaudeDecisionMaker:
    """Claude AI-powered trading decision maker"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY") or os.getenv("CLAUDE_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY or CLAUDE_API_KEY not found")
            
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = "claude-3-opus-20240229"  # Using Claude 3 Opus for best performance
        self.system_prompt = self._create_system_prompt()
        
    def _create_system_prompt(self) -> str:
        """Create the system prompt for Claude"""
        # Check if we're in paper mode for more aggressive trading
        is_paper_mode = os.getenv("TRADING_MODE", "simulation") in ["paper", "simulation"]
        
        if is_paper_mode:
            return """You are an expert options trading advisor in PAPER TRADING MODE (not real money).

Your role is to ACTIVELY TRADE opportunities for testing and learning purposes.

PAPER TRADING RULES - BE AGGRESSIVE:
1. If confidence >= 0.70, you should TRADE (not HOLD)
2. If confidence >= 0.85, you MUST trade - these are urgent opportunities
3. Manual signals from JSON files are pre-screened - ACT ON THEM
4. This is for TESTING - favor action over inaction
5. We need to see trades execute to validate the system

Decision Framework:
- BUY_CALL: Use when signal confidence > 0.70 and bullish
- BUY_PUT: Use when signal confidence > 0.70 and bearish  
- HOLD: Only when confidence < 0.70 or major red flags

IMPORTANT: Since this is paper trading, take more trades to test the system.
The goal is to validate order execution, not maximize paper profits.

Output Format: Return a valid JSON object with the decision details."""
        else:
            return """You are an expert options trading advisor with deep knowledge of market dynamics, technical analysis, and risk management.

Your role is to analyze trading opportunities and provide actionable decisions for options trading.

Key principles:
1. Risk Management: Never risk more than 2% of portfolio on a single trade
2. Probability Focus: Look for high-probability setups with favorable risk/reward
3. Market Context: Consider overall market conditions and correlations
4. Sentiment Analysis: Weight social signals and news sentiment appropriately
5. Technical Confirmation: Require technical indicator alignment for entries

Decision Framework:
- BUY_CALL: Bullish outlook with upward momentum
- BUY_PUT: Bearish outlook or hedging needs
- SELL: Close existing position (profit or stop loss)
- HOLD: Insufficient edge or unclear signals

For each decision, provide:
1. Clear action with specific parameters
2. Confidence level (0-1)
3. Detailed reasoning
4. Risk assessment
5. Expected outcome with timeframe

Output Format: Return a valid JSON object with the decision details."""
        
    async def make_decision(self, context: TradingContext) -> TradingDecision:
        """Make a trading decision based on context"""
        
        # Prepare the analysis prompt
        analysis_prompt = self._prepare_analysis_prompt(context)
        
        try:
            # Call Claude API
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                temperature=0.3,  # Lower temperature for more consistent decisions
                system=self.system_prompt,
                messages=[
                    {"role": "user", "content": analysis_prompt}
                ]
            )
            
            # Parse response
            decision = self._parse_response(response.content[0].text)
            
            # Validate decision
            if self._validate_decision(decision, context):
                logger.info(f"AI Decision: {decision.action} for {decision.ticker}")
                return decision
            else:
                logger.warning("AI decision failed validation, returning HOLD")
                return self._create_hold_decision(context.ticker, "Decision failed validation")
                
        except Exception as e:
            logger.error(f"Error making AI decision: {e}")
            return self._create_hold_decision(context.ticker, f"Error: {str(e)}")
            
    def _prepare_analysis_prompt(self, context: TradingContext) -> str:
        """Prepare the analysis prompt for Claude"""
        
        # Calculate key metrics
        whatsapp_sentiment = self._calculate_signal_sentiment(context.whatsapp_signals)
        position_size = self._calculate_position_size(context.portfolio_state)
        
        prompt = f"""Analyze this trading opportunity and provide a decision:

TICKER: {context.ticker}
CURRENT PRICE: ${context.current_price}
TIMESTAMP: {context.timestamp}

MARKET CONDITIONS:
{json.dumps(context.market_conditions, indent=2)}

WHATSAPP GROUP SIGNALS ({len(context.whatsapp_signals)} signals):
- Overall Sentiment: {whatsapp_sentiment}
- Recent Signals: {json.dumps(context.whatsapp_signals[:5], indent=2)}

NEWS SENTIMENT:
{json.dumps(context.news_sentiment, indent=2)}

TECHNICAL INDICATORS:
{json.dumps(context.technical_indicators, indent=2)}

PORTFOLIO STATE:
- Total Value: ${context.portfolio_state.get('total_value', 100000)}
- Cash Available: ${context.portfolio_state.get('cash', 50000)}
- Current Positions: {context.portfolio_state.get('position_count', 0)}
- Suggested Position Size: {position_size}%

RECENT PERFORMANCE:
{json.dumps(context.recent_performance, indent=2)}

RISK METRICS:
{json.dumps(context.risk_metrics, indent=2)}

Based on this analysis, provide your trading decision in JSON format:
{{
    "action": "BUY_CALL|BUY_PUT|SELL|HOLD",
    "ticker": "{context.ticker}",
    "option_type": "CALL|PUT|null",
    "strike_price": null or number,
    "expiration_days": null or number (typically 30-45),
    "quantity": number of contracts,
    "confidence": 0.0 to 1.0,
    "reasoning": "detailed explanation",
    "risk_assessment": "risk analysis",
    "expected_outcome": "what you expect to happen",
    "stop_loss": null or price level,
    "take_profit": null or price level
}}"""
        
        return prompt
        
    def _calculate_signal_sentiment(self, signals: List[Dict]) -> str:
        """Calculate overall sentiment from signals"""
        if not signals:
            return "NEUTRAL"
            
        bullish = sum(1 for s in signals if s.get("signal_type") == "BULLISH")
        bearish = sum(1 for s in signals if s.get("signal_type") == "BEARISH")
        
        if bullish > bearish * 1.5:
            return f"BULLISH ({bullish}/{len(signals)})"
        elif bearish > bullish * 1.5:
            return f"BEARISH ({bearish}/{len(signals)})"
        else:
            return f"NEUTRAL ({bullish}B/{bearish}S)"
            
    def _calculate_position_size(self, portfolio: Dict) -> float:
        """Calculate appropriate position size as percentage"""
        total_value = portfolio.get("total_value", 100000)
        cash = portfolio.get("cash", 50000)
        
        # Kelly Criterion simplified: 2-5% per position
        base_size = 0.02  # 2% base
        
        # Adjust based on available cash
        if cash / total_value > 0.5:
            base_size = 0.03  # More aggressive with more cash
        elif cash / total_value < 0.2:
            base_size = 0.01  # Conservative with less cash
            
        return round(base_size * 100, 1)
        
    def _parse_response(self, response_text: str) -> TradingDecision:
        """Parse Claude's response into TradingDecision"""
        
        try:
            # Extract JSON from response
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1
            json_str = response_text[json_start:json_end]
            
            decision_data = json.loads(json_str)
            
            return TradingDecision(
                action=decision_data.get("action", "HOLD"),
                ticker=decision_data.get("ticker", ""),
                option_type=decision_data.get("option_type"),
                strike_price=decision_data.get("strike_price"),
                expiration_days=decision_data.get("expiration_days"),
                quantity=decision_data.get("quantity", 1),
                confidence=decision_data.get("confidence", 0.5),
                reasoning=decision_data.get("reasoning", ""),
                risk_assessment=decision_data.get("risk_assessment", ""),
                expected_outcome=decision_data.get("expected_outcome", ""),
                stop_loss=decision_data.get("stop_loss"),
                take_profit=decision_data.get("take_profit")
            )
        except Exception as e:
            logger.error(f"Failed to parse AI response: {e}")
            raise
            
    def _validate_decision(self, decision: TradingDecision, context: TradingContext) -> bool:
        """Validate the AI decision"""
        
        # Check confidence threshold (lower for paper trading)
        is_paper_mode = os.getenv("TRADING_MODE", "simulation") in ["paper", "simulation"]
        min_confidence = 0.4 if is_paper_mode else 0.6
        
        if decision.confidence < min_confidence:
            logger.info(f"Decision confidence too low: {decision.confidence} (min: {min_confidence})")
            return False
            
        # Check action validity
        valid_actions = ["BUY_CALL", "BUY_PUT", "SELL", "HOLD"]
        if decision.action not in valid_actions:
            logger.error(f"Invalid action: {decision.action}")
            return False
            
        # Check position size
        if decision.quantity > 10:
            logger.warning(f"Position size too large: {decision.quantity}")
            decision.quantity = 10  # Cap at 10 contracts
            
        # Validate strike price for options
        if decision.action in ["BUY_CALL", "BUY_PUT"]:
            if not decision.strike_price or decision.strike_price <= 0:
                logger.error("Invalid strike price for options trade")
                return False
                
            # Check strike is within reasonable range (±20% of current price)
            price_diff = abs(decision.strike_price - context.current_price) / context.current_price
            if price_diff > 0.2:
                logger.warning(f"Strike price too far from current: {price_diff:.1%}")
                return False
                
        return True
        
    def _create_hold_decision(self, ticker: str, reason: str) -> TradingDecision:
        """Create a default HOLD decision"""
        return TradingDecision(
            action="HOLD",
            ticker=ticker,
            option_type=None,
            strike_price=None,
            expiration_days=None,
            quantity=0,
            confidence=0.5,
            reasoning=reason,
            risk_assessment="No action taken",
            expected_outcome="Waiting for better opportunity",
            stop_loss=None,
            take_profit=None
        )
        
    async def analyze_batch(self, tickers: List[str], market_data: Dict) -> List[TradingDecision]:
        """Analyze multiple tickers and return decisions"""
        
        decisions = []
        
        for ticker in tickers:
            # Create context for each ticker
            context = TradingContext(
                timestamp=datetime.now(),
                ticker=ticker,
                current_price=market_data.get(ticker, {}).get("price", 100),
                market_conditions=market_data.get("conditions", {}),
                whatsapp_signals=[],  # Would be populated from data sources
                news_sentiment={},
                technical_indicators={},
                recent_performance={},
                portfolio_state=market_data.get("portfolio", {}),
                risk_metrics={}
            )
            
            decision = await self.make_decision(context)
            decisions.append(decision)
            
            # Rate limiting
            await asyncio.sleep(1)  # Respect API rate limits
            
        return decisions
        
    def explain_decision(self, decision: TradingDecision) -> str:
        """Generate human-readable explanation of decision"""
        
        explanation = f"""
📊 TRADING DECISION for {decision.ticker}
{'='*50}

🎯 Action: {decision.action}
📈 Confidence: {decision.confidence:.1%}

"""
        
        if decision.action in ["BUY_CALL", "BUY_PUT"]:
            explanation += f"""📋 Details:
- Option Type: {decision.option_type}
- Strike Price: ${decision.strike_price}
- Expiration: {decision.expiration_days} days
- Quantity: {decision.quantity} contracts
"""
            
        if decision.stop_loss:
            explanation += f"- Stop Loss: ${decision.stop_loss}\n"
        if decision.take_profit:
            explanation += f"- Take Profit: ${decision.take_profit}\n"
            
        explanation += f"""
💭 Reasoning:
{decision.reasoning}

⚠️ Risk Assessment:
{decision.risk_assessment}

🎯 Expected Outcome:
{decision.expected_outcome}
"""
        
        return explanation


# Example usage
async def test_claude_decision_maker():
    """Test the Claude decision maker"""
    
    # Note: Requires ANTHROPIC_API_KEY environment variable
    # decision_maker = ClaudeDecisionMaker()
    
    # Mock decision for testing without API key
    mock_decision = TradingDecision(
        action="BUY_CALL",
        ticker="AAPL",
        option_type="CALL",
        strike_price=180.0,
        expiration_days=30,
        quantity=2,
        confidence=0.75,
        reasoning="Strong bullish signals from WhatsApp group combined with positive technical indicators",
        risk_assessment="Moderate risk with defined stop loss",
        expected_outcome="Expect 15-20% gain within 2 weeks",
        stop_loss=175.0,
        take_profit=185.0
    )
    
    print("\n" + "="*60)
    print("CLAUDE AI DECISION MAKER TEST")
    print("="*60)
    
    # Test explanation
    explanation = ClaudeDecisionMaker("test_key").explain_decision(mock_decision)
    print(explanation)
    
    print("\n✅ Decision maker ready for integration!")
    print("   Set ANTHROPIC_API_KEY environment variable to enable")


if __name__ == "__main__":
    asyncio.run(test_claude_decision_maker())