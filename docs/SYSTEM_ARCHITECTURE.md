# System Architecture - AI Options Trading Bot

## Complete System Flow

```mermaid
graph TB
    subgraph "Trigger Layer"
        GHA[GitHub Actions<br/>Every 3 hours]
        Manual[Manual Trigger]
    end

    subgraph "Data Collection Layer"
        Market[Market Data<br/>Alpaca API]
        News[News Data<br/>NewsAPI]
        Social[Social Sentiment<br/>Reddit/Twitter]
        Historic[Historical Signals<br/>Supabase DB]
    end

    subgraph "Analysis Layer"
        TechAnalysis[Technical Indicators<br/>RSI, MACD, Bollinger]
        OptionsAnalysis[Options Analysis<br/>Greeks, IV, Volume]
        SentimentAnalysis[Sentiment Score<br/>News + Social]
        PatternRecog[Pattern Recognition<br/>Historical Patterns]
    end

    subgraph "Decision Engine"
        SignalGen[Signal Generator<br/>Combine All Inputs]
        Claude[Claude AI<br/>Decision Making]
        RiskMgmt[Risk Management<br/>Position Sizing]
        Confidence[Confidence Score<br/>0-100%]
    end

    subgraph "Execution Layer"
        OrderMgmt[Order Management]
        Alpaca[Alpaca Trading<br/>Paper/Live]
        PositionTrack[Position Tracking]
    end

    subgraph "Storage Layer"
        Supabase[(Supabase PostgreSQL<br/>Cloud Database)]
        Logs[GitHub Actions Logs]
    end

    subgraph "Monitoring"
        Dashboard[Alpaca Dashboard]
        GitHubMon[GitHub Actions Monitor]
        SupabaseMon[Supabase Dashboard]
    end

    GHA --> Market
    Manual --> Market
    
    Market --> TechAnalysis
    News --> SentimentAnalysis
    Social --> SentimentAnalysis
    Historic --> PatternRecog
    
    TechAnalysis --> SignalGen
    OptionsAnalysis --> SignalGen
    SentimentAnalysis --> SignalGen
    PatternRecog --> SignalGen
    
    SignalGen --> Claude
    Claude --> RiskMgmt
    RiskMgmt --> Confidence
    
    Confidence -->|Score > 70%| OrderMgmt
    Confidence -->|Score < 70%| Supabase
    
    OrderMgmt --> Alpaca
    Alpaca --> PositionTrack
    PositionTrack --> Supabase
    
    Supabase --> Historic
    OrderMgmt --> Logs
    
    Alpaca --> Dashboard
    GHA --> GitHubMon
    Supabase --> SupabaseMon

    style GHA fill:#90EE90
    style Claude fill:#FFE4B5
    style Supabase fill:#87CEEB
    style Alpaca fill:#FFB6C1
```

## Trading Decision Flow

```mermaid
flowchart LR
    Start([Market Data]) --> Analyze{Analyze Signals}
    
    Analyze --> Momentum[Momentum<br/>RSI < 30 or > 70]
    Analyze --> Volatility[Volatility<br/>IV Percentile]
    Analyze --> Trend[Trend<br/>MA Crossover]
    
    Momentum --> Signals[Generate Signals]
    Volatility --> Signals
    Trend --> Signals
    
    Signals --> Claude{Claude AI<br/>Decision}
    
    Claude -->|High Confidence| Trade[Execute Trade]
    Claude -->|Low Confidence| Skip[Skip Trade]
    
    Trade --> Monitor[Monitor Position]
    Skip --> Wait[Wait for Next Cycle]
    
    Monitor --> Exit{Exit Conditions}
    Exit -->|Stop Loss| Close[Close Position]
    Exit -->|Take Profit| Close
    Exit -->|Time Stop| Close
    Exit -->|Hold| Monitor
    
    Close --> Record[Record Results]
    Record --> Learn[Update ML Model]
    Learn --> Wait
    
    Wait --> Start
```

## Data Flow Diagram

```mermaid
graph LR
    subgraph "Input Sources"
        A1[Alpaca Market Data]
        A2[Options Chain]
        A3[News API]
        A4[Social Media]
    end
    
    subgraph "Processing"
        B1[Data Aggregator]
        B2[Signal Processor]
        B3[Risk Calculator]
    end
    
    subgraph "Decision"
        C1[Strategy Engine]
        C2[Claude AI]
        C3[Confidence Scorer]
    end
    
    subgraph "Output"
        D1[Trade Execution]
        D2[Database Storage]
        D3[Monitoring Alerts]
    end
    
    A1 --> B1
    A2 --> B1
    A3 --> B1
    A4 --> B1
    
    B1 --> B2
    B2 --> C1
    B2 --> C2
    
    C1 --> C3
    C2 --> C3
    
    C3 --> D1
    C3 --> D2
    
    D1 --> D3
    D2 --> B3
    B3 --> C3
```

## Testing Architecture

```mermaid
graph TD
    subgraph "Testing Modes"
        Sim[Full Simulation<br/>No Market Connection]
        Paper[Paper Trading<br/>Real Market Data]
        Live[Live Trading<br/>Real Money]
    end
    
    subgraph "Test Types"
        Unit[Unit Tests]
        Integration[Integration Tests]
        Hypothesis[Hypothesis Tests]
        Backtest[Backtesting]
    end
    
    subgraph "Validation"
        Metrics[Performance Metrics]
        Risk[Risk Analysis]
        Confidence[Strategy Validation]
    end
    
    Sim --> Unit
    Sim --> Hypothesis
    
    Paper --> Integration
    Paper --> Backtest
    
    Unit --> Metrics
    Integration --> Metrics
    Hypothesis --> Confidence
    Backtest --> Risk
    
    Metrics --> Decision{Ready for Production?}
    Risk --> Decision
    Confidence --> Decision
    
    Decision -->|Yes| Live
    Decision -->|No| Sim
```

## Database Schema

```mermaid
erDiagram
    SIGNALS ||--o{ TRADES : generates
    TRADES ||--o{ POSITION_UPDATES : has
    TRADES }o--|| DECISION_LOGS : logged_by
    MARKET_SNAPSHOTS ||--o{ SIGNALS : influences
    
    SIGNALS {
        int id PK
        string symbol
        string signal_type
        float confidence
        decimal strike_price
        datetime expiration
        float implied_volatility
        boolean trade_executed
        decimal profit_loss
    }
    
    TRADES {
        int id PK
        string order_id
        string symbol
        int quantity
        string side
        decimal filled_price
        string status
        decimal realized_pnl
    }
    
    POSITION_UPDATES {
        int id PK
        int trade_id FK
        decimal current_price
        decimal unrealized_pnl
        float delta
        float gamma
        float theta
        float vega
    }
    
    DECISION_LOGS {
        int id PK
        string symbol
        string action
        json market_data
        text claude_response
        float confidence_score
    }
    
    MARKET_SNAPSHOTS {
        int id PK
        decimal spy_price
        float vix_level
        float put_call_ratio
        float fear_greed_index
    }
```

## Deployment Pipeline

```mermaid
graph LR
    subgraph "Development"
        Local[Local Development]
        Test[Run Tests]
        Sim[Simulation Testing]
    end
    
    subgraph "CI/CD"
        Push[Git Push]
        Actions[GitHub Actions]
        Build[Build & Test]
    end
    
    subgraph "Production"
        Deploy[Deploy Container]
        Schedule[Cron Schedule]
        Execute[Execute Trades]
    end
    
    subgraph "Monitoring"
        Logs[Action Logs]
        Database[Database Metrics]
        Performance[P&L Tracking]
    end
    
    Local --> Test
    Test --> Sim
    Sim --> Push
    
    Push --> Actions
    Actions --> Build
    Build --> Deploy
    
    Deploy --> Schedule
    Schedule --> Execute
    
    Execute --> Logs
    Execute --> Database
    Database --> Performance
    
    Performance -->|Feedback| Local
```

## Risk Management Flow

```mermaid
flowchart TD
    Start([New Signal]) --> Check1{Portfolio Risk Check}
    
    Check1 -->|Pass| Check2{Position Size Check}
    Check1 -->|Fail| Reject[Reject Trade]
    
    Check2 -->|Pass| Check3{Daily Loss Check}
    Check2 -->|Fail| Reduce[Reduce Size]
    
    Check3 -->|Pass| Check4{Correlation Check}
    Check3 -->|Fail| Reject
    
    Check4 -->|Pass| Execute[Execute Trade]
    Check4 -->|Fail| Reject
    
    Reduce --> Check3
    
    Execute --> Monitor{Monitor Position}
    
    Monitor --> StopLoss{Stop Loss Hit?}
    StopLoss -->|Yes| Close[Close Position]
    StopLoss -->|No| TakeProfit{Take Profit Hit?}
    
    TakeProfit -->|Yes| Close
    TakeProfit -->|No| TimeStop{Time Stop Hit?}
    
    TimeStop -->|Yes| Close
    TimeStop -->|No| Monitor
    
    Close --> Record[Record Results]
    Reject --> Record
```

## System Components Summary

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Scheduler** | GitHub Actions | Run every 3 hours |
| **Market Data** | Alpaca API | Real-time prices & options |
| **Database** | Supabase PostgreSQL | Store signals & trades |
| **AI Decision** | Claude API | Analyze & decide |
| **Execution** | Alpaca Trading API | Place trades |
| **Simulation** | Python Custom | Test strategies |
| **Monitoring** | GitHub/Supabase/Alpaca | Track performance |
| **Container** | Docker | Deployment |

## Key Features

- 🤖 **AI-Driven**: Claude analyzes all signals
- 📊 **Multi-Source Data**: Market, news, social sentiment
- 🎯 **Options Focus**: Specialized for options trading
- 🔄 **Automated**: Runs every 3 hours via GitHub Actions
- 📈 **Learning System**: Improves from historical data
- 🛡️ **Risk Management**: Multiple safety checks
- 🧪 **Dual Testing**: Simulation + Paper trading
- ☁️ **Cloud Native**: Fully cloud-based architecture