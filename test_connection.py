#!/usr/bin/env python3
"""Test MySQL connection"""

from steam_explorer.config import get_settings
from steam_explorer.db import get_engine
from sqlalchemy import text

def test_connection():
    try:
        settings = get_settings()
        print(f"Testing connection to: {settings.database_url}")
        
        engine = get_engine(settings.database_url)
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT VERSION()"))
            version = result.fetchone()[0]
            print(f"✅ Connected successfully!")
            print(f"MySQL version: {version}")
            
        print("✅ Connection test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    test_connection()