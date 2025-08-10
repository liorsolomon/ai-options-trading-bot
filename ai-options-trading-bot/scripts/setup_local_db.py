#!/usr/bin/env python3
"""
Set up a local SQLite database for development/testing
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))


def setup_sqlite():
    """Set up SQLite database for local development"""
    
    print("🔧 Setting up local SQLite database...")
    
    # Create data directory
    data_dir = Path(__file__).parent.parent / "data"
    data_dir.mkdir(exist_ok=True)
    
    # SQLite database path
    db_path = data_dir / "trading_bot.db"
    
    # Update .env file
    env_path = Path(__file__).parent.parent / ".env"
    
    if env_path.exists():
        with open(env_path, "r") as f:
            lines = f.readlines()
        
        # Update DATABASE_URL line
        updated = False
        for i, line in enumerate(lines):
            if line.startswith("DATABASE_URL="):
                lines[i] = f'DATABASE_URL=sqlite:///{db_path.absolute()}\n'
                updated = True
                break
        
        if not updated:
            lines.append(f'\nDATABASE_URL=sqlite:///{db_path.absolute()}\n')
        
        with open(env_path, "w") as f:
            f.writelines(lines)
        
        print(f"✅ Updated .env with SQLite database path")
    else:
        # Create .env file
        with open(env_path, "w") as f:
            f.write(f'DATABASE_URL=sqlite:///{db_path.absolute()}\n')
        print(f"✅ Created .env with SQLite database path")
    
    print(f"📁 Database will be created at: {db_path}")
    
    # Now initialize the database
    from dotenv import load_dotenv
    load_dotenv(override=True)
    
    # Import after loading env
    import asyncio
    from src.database.connection import DatabaseManager
    
    async def create_tables():
        # For SQLite, we need to use sync URL
        db_url = f"sqlite:///{db_path.absolute()}"
        os.environ["DATABASE_URL"] = db_url
        
        try:
            # Create tables using sync engine for SQLite
            from sqlalchemy import create_engine
            from src.database.models import Base
            
            engine = create_engine(db_url, echo=False)
            Base.metadata.create_all(engine)
            
            print("✅ Database tables created successfully!")
            
            # List tables
            from sqlalchemy import inspect
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            
            print(f"\n📊 Created {len(tables)} tables:")
            for table in tables:
                print(f"   - {table}")
            
            engine.dispose()
            
            return True
            
        except Exception as e:
            print(f"❌ Error creating tables: {e}")
            return False
    
    # Run the async function
    success = asyncio.run(create_tables())
    
    if success:
        print("\n✅ Local SQLite database setup complete!")
        print("\nYou can now run the trading bot locally.")
        print("The database file is located at:", db_path)
        print("\nNote: For production, use PostgreSQL (Supabase/Neon)")
    
    return success


if __name__ == "__main__":
    setup_sqlite()