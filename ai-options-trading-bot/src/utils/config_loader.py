"""
Configuration loader with environment-specific settings
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any
from loguru import logger


def load_config() -> Dict[str, Any]:
    """Load configuration from files and environment"""
    
    # Load strategy config
    config_path = Path(__file__).parent.parent.parent / "config" / "strategies.yaml"
    
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    
    # Add environment variables
    config["env"] = {
        "alpaca_api_key": os.getenv("ALPACA_API_KEY"),
        "alpaca_secret_key": os.getenv("ALPACA_SECRET_KEY"),
        "alpaca_base_url": os.getenv("ALPACA_BASE_URL", "https://paper-api.alpaca.markets"),
        "database_url": os.getenv("DATABASE_URL"),
        "claude_api_key": os.getenv("CLAUDE_API_KEY"),
        "trading_mode": os.getenv("TRADING_MODE", "paper"),
        "environment": os.getenv("ENVIRONMENT", "development"),
        "log_level": os.getenv("LOG_LEVEL", "INFO"),
    }
    
    # Validate critical configuration
    if not config["env"]["database_url"]:
        logger.warning("DATABASE_URL not set - using local SQLite")
        # Default to local SQLite for development
        db_path = Path(__file__).parent.parent.parent / "data" / "trading_bot.db"
        db_path.parent.mkdir(exist_ok=True)
        config["env"]["database_url"] = f"sqlite:///{db_path}"
    
    # Check if running in GitHub Actions
    if os.getenv("GITHUB_ACTIONS") == "true":
        logger.info("Running in GitHub Actions environment")
        config["env"]["is_github_actions"] = True
        
        # Ensure cloud database for GitHub Actions
        if "sqlite" in config["env"]["database_url"]:
            raise ValueError(
                "Cannot use SQLite in GitHub Actions! "
                "Please set up a cloud database (Supabase/Neon). "
                "See docs/CLOUD_DATABASE_SETUP.md for instructions."
            )
    else:
        config["env"]["is_github_actions"] = False
    
    # Trading limits from environment
    config["limits"] = {
        "max_position_size": int(os.getenv("MAX_POSITION_SIZE", "1000")),
        "max_daily_loss": int(os.getenv("MAX_DAILY_LOSS", "500")),
        "max_open_positions": int(os.getenv("MAX_OPEN_POSITIONS", "5")),
    }
    
    return config


def validate_config(config: Dict[str, Any]) -> bool:
    """Validate configuration is complete"""
    
    required_keys = [
        "env.alpaca_api_key",
        "env.alpaca_secret_key",
        "env.database_url",
    ]
    
    for key_path in required_keys:
        keys = key_path.split(".")
        value = config
        for key in keys:
            if key not in value or not value[key]:
                logger.error(f"Missing required configuration: {key_path}")
                return False
            value = value[key]
    
    return True


def get_database_url() -> str:
    """Get database URL with fallback logic"""
    
    # Check for GitHub Actions
    if os.getenv("GITHUB_ACTIONS") == "true":
        db_url = os.getenv("DATABASE_URL")
        if not db_url or "sqlite" in db_url.lower():
            raise ValueError(
                "GitHub Actions requires a cloud database! "
                "SQLite will not persist data between runs. "
                "Please set DATABASE_URL to a PostgreSQL database. "
                "See: https://github.com/yourusername/ai-options-trading-bot/blob/main/docs/CLOUD_DATABASE_SETUP.md"
            )
        return db_url
    
    # Local development
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        # Create local SQLite database
        db_path = Path(__file__).parent.parent.parent / "data" / "trading_bot.db"
        db_path.parent.mkdir(exist_ok=True)
        db_url = f"sqlite:///{db_path}"
        logger.info(f"Using local SQLite database: {db_path}")
    
    return db_url