# AI Options Trading Bot - System Architecture

## 🏗️ High-Level System Overview

```mermaid
graph TB
    subgraph "📅 Schedule"
        Timer[⏰ Every 3 Hours<br/>GitHub Actions]
    end
    
    subgraph "📊 Data Collection"
        Markets[📈 Market Data]
        Options[📊 Options Chains]
        News[📰 News Sentiment]
    end
    
    subgraph "🧠 Intelligence"
        Analysis[📉 Technical Analysis]
        Claude[🤖 Claude AI]
        Signals[🎯 Signal Generation]
    end
    
    subgraph "💼 Trading"
        Decision[✅ Trade Decision]
        Alpaca[🏦 Alpaca Broker]
        Position[📍 Position Management]
    end
    
    subgraph "💾 Storage"
        Database[(☁️ Supabase DB)]
    end
    
    Timer --> Markets
    Markets --> Analysis
    Options --> Analysis
    News --> Analysis
    
    Analysis --> Claude
    Claude --> Signals
    Signals --> Decision
    
    Decision -->|Execute| Alpaca
    Decision -->|Record| Database
    
    Alpaca --> Position
    Position --> Database
    Database -->|Learn| Analysis
    
    style Timer fill:#FFE4B5
    style Claude fill:#E6E6FA
    style Database fill:#90EE90
    style Alpaca fill:#FFB6C1
```

## 🔄 Simple Trading Flow

```mermaid
flowchart LR
    A[📊 Get Data] --> B[🤔 Analyze]
    B --> C{🤖 Claude<br/>Decides}
    C -->|Buy Signal| D[📈 Buy Option]
    C -->|Sell Signal| E[📉 Sell Option]
    C -->|No Signal| F[⏸️ Wait]
    D --> G[💾 Save Result]
    E --> G
    F --> G
    G --> H[🔄 Repeat in 3hrs]
```

## 🧪 Testing Modes

```mermaid
graph LR
    subgraph "Development Flow"
        A[🧑‍💻 Write Code] --> B[🧪 Simulation Test]
        B --> C[📝 Paper Trading]
        C --> D[💰 Live Trading]
    end
    
    B -->|Instant| B1[✅ No Market Hours]
    C -->|Real Data| C1[✅ Safe Testing]
    D -->|Ready| D1[✅ Real Money]
```

## 📦 Tech Stack

| Component | Technology |
|-----------|------------|
| 🤖 **AI Brain** | Claude API |
| 📊 **Trading** | Alpaca Markets |
| 💾 **Database** | Supabase (PostgreSQL) |
| ⚙️ **Automation** | GitHub Actions |
| 🐍 **Language** | Python |
| 🧪 **Testing** | Custom Simulator |

## 🎯 Key Features

- **Automated**: Runs every 3 hours automatically
- **Intelligent**: Claude AI makes trading decisions
- **Safe**: Paper trading with virtual money
- **Learning**: Improves from historical data
- **Flexible**: Works with stocks and options
- **Cloud-Based**: No local server needed

## 🚀 Quick Start

1. **Clone** → 2. **Configure** → 3. **Test** → 4. **Deploy**

The bot handles everything else automatically!