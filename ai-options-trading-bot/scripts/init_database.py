#!/usr/bin/env python3
"""
Initialize the database with tables and sample data
"""

import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path - handle both local and GitHub Actions
script_dir = Path(__file__).parent
project_root = script_dir.parent

# Try different path configurations
if (project_root / 'src').exists():
    sys.path.insert(0, str(project_root))
elif (project_root / 'ai-options-trading-bot' / 'src').exists():
    sys.path.insert(0, str(project_root / 'ai-options-trading-bot'))
else:
    # Fallback - go up one more level
    sys.path.insert(0, str(project_root.parent))

load_dotenv()

from src.database.connection import DatabaseManager
from src.database.models import Base
from loguru import logger


async def init_database():
    """Initialize database with all tables"""
    
    logger.info("Starting database initialization...")
    
    # Check if DATABASE_URL is set
    db_url = os.getenv("DATABASE_URL")
    if not db_url or db_url == "postgresql://user:password@host:5432/trading_bot_db":
        logger.warning("=" * 60)
        logger.warning("DATABASE_URL not configured!")
        logger.warning("Please set up a PostgreSQL database first.")
        logger.warning("")
        logger.warning("Options:")
        logger.warning("1. Supabase (Recommended - Free)")
        logger.warning("   - Sign up at https://supabase.com")
        logger.warning("   - Create a new project")
        logger.warning("   - Get connection string from Settings → Database")
        logger.warning("")
        logger.warning("2. Neon (Alternative - Free)")
        logger.warning("   - Sign up at https://neon.tech")
        logger.warning("   - Create a new project")
        logger.warning("   - Copy the connection string")
        logger.warning("")
        logger.warning("3. Local PostgreSQL")
        logger.warning("   - Install PostgreSQL locally")
        logger.warning("   - Create a database: createdb trading_bot_db")
        logger.warning("   - Update .env with your connection string")
        logger.warning("=" * 60)
        return False
    
    try:
        # Initialize database manager
        db_manager = DatabaseManager(db_url)
        
        # Create all tables
        logger.info("Creating database tables...")
        await db_manager.create_tables()
        
        logger.success("✅ Database tables created successfully!")
        
        # Verify tables were created
        async with db_manager.get_session() as session:
            # Test query
            from sqlalchemy import text
            result = await session.execute(text("SELECT tablename FROM pg_tables WHERE schemaname='public'"))
            tables = [row[0] for row in result]
            
            logger.info(f"Created {len(tables)} tables:")
            for table in tables:
                logger.info(f"  - {table}")
        
        # Close connections
        await db_manager.close()
        
        logger.success("✅ Database initialization complete!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        logger.error("Please check your DATABASE_URL and ensure the database is accessible")
        return False


async def reset_database():
    """Reset database (drop and recreate all tables)"""
    
    logger.warning("⚠️  This will DELETE all data in the database!")
    response = input("Are you sure you want to continue? (yes/no): ")
    
    if response.lower() != "yes":
        logger.info("Database reset cancelled")
        return
    
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        logger.error("DATABASE_URL not set")
        return
    
    try:
        db_manager = DatabaseManager(db_url)
        
        # Drop all tables
        logger.info("Dropping all tables...")
        await db_manager.drop_tables()
        
        # Recreate tables
        logger.info("Creating new tables...")
        await db_manager.create_tables()
        
        await db_manager.close()
        
        logger.success("✅ Database reset complete!")
        
    except Exception as e:
        logger.error(f"❌ Database reset failed: {e}")


async def test_connection():
    """Test database connection"""
    
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        logger.error("DATABASE_URL not set")
        return False
    
    try:
        db_manager = DatabaseManager(db_url)
        
        async with db_manager.get_session() as session:
            from sqlalchemy import text
            result = await session.execute(text("SELECT 1"))
            logger.success("✅ Database connection successful!")
        
        await db_manager.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False


def main():
    """Main entry point"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="Database management tool")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Reset database (drop and recreate all tables)"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Test database connection"
    )
    
    args = parser.parse_args()
    
    if args.reset:
        asyncio.run(reset_database())
    elif args.test:
        asyncio.run(test_connection())
    else:
        asyncio.run(init_database())


if __name__ == "__main__":
    main()