#!/usr/bin/env python3
"""Add game_name column to ownerships table and populate it"""

import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from steam_explorer.config import get_settings
from steam_explorer.db import get_sessionmaker
from steam_explorer.models import Ownership, Game
from sqlalchemy import text

def add_game_name_column():
    settings = get_settings()
    SessionLocal = get_sessionmaker(settings.database_url)
    
    with SessionLocal() as session:
        try:
            # Add the column (will fail if it already exists)
            session.execute(text("ALTER TABLE ownerships ADD COLUMN game_name VARCHAR(255)"))
            print("✅ Added game_name column to ownerships table")
        except Exception as e:
            if "Duplicate column name" in str(e) or "already exists" in str(e):
                print("ℹ️  game_name column already exists")
            else:
                print(f"Error adding column: {e}")
                return
        
        # Update existing records with game names
        print("🔄 Updating ownership records with game names...")
        
        # Get all ownerships that don't have game names
        ownerships = session.query(Ownership).filter(
            (Ownership.game_name.is_(None)) | (Ownership.game_name == '')
        ).all()
        
        updated_count = 0
        for ownership in ownerships:
            # Find the corresponding game
            game = session.query(Game).filter(Game.appid == ownership.appid).first()
            
            if game:
                ownership.game_name = game.name
                updated_count += 1
            else:
                ownership.game_name = f"Unknown Game ({ownership.appid})"
        
        session.commit()
        print(f"✅ Updated {updated_count} ownership records with game names")
        
        # Show sample data
        sample_ownerships = session.query(Ownership).filter(
            Ownership.playtime_forever > 0
        ).order_by(Ownership.playtime_forever.desc()).limit(5).all()
        
        print(f"\n=== Sample Updated Data ===")
        print(f"{'Game Name':<40} {'Hours':<8} {'Minutes'}")
        print("-" * 60)
        
        for ownership in sample_ownerships:
            game_name = ownership.game_name[:37] + "..." if len(ownership.game_name) > 40 else ownership.game_name
            hours = round(ownership.playtime_forever / 60, 1) if ownership.playtime_forever else 0
            minutes = ownership.playtime_forever or 0
            print(f"{game_name:<40} {hours:<8} {minutes}")

def main():
    add_game_name_column()

if __name__ == "__main__":
    main()