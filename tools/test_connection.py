#!/usr/bin/env python3
"""Test database connection"""

import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from steam_explorer.config import get_settings
from steam_explorer.db import get_engine
from sqlalchemy import text

def test_connection():
    try:
        settings = get_settings()
        print(f"Testing connection to: {settings.database_url}")
        
        engine = get_engine(settings.database_url)
        
        with engine.connect() as conn:
            if "mysql" in settings.database_url.lower():
                result = conn.execute(text("SELECT VERSION()"))
                version = result.fetchone()[0]
                print(f"✅ Connected successfully!")
                print(f"MySQL version: {version}")
            elif "postgresql" in settings.database_url.lower():
                result = conn.execute(text("SELECT version()"))
                version = result.fetchone()[0]
                print(f"✅ Connected successfully!")
                print(f"PostgreSQL version: {version}")
            else:
                result = conn.execute(text("SELECT sqlite_version()"))
                version = result.fetchone()[0]
                print(f"✅ Connected successfully!")
                print(f"SQLite version: {version}")
            
        print("✅ Connection test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def main():
    test_connection()

if __name__ == "__main__":
    main()