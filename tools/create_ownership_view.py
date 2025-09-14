#!/usr/bin/env python3
"""Create a database view that joins ownerships with game names"""

import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from steam_explorer.config import get_settings
from steam_explorer.db import get_sessionmaker
from sqlalchemy import text

def create_ownership_view():
    settings = get_settings()
    SessionLocal = get_sessionmaker(settings.database_url)
    
    with SessionLocal() as session:
        # Drop view if it exists
        session.execute(text("DROP VIEW IF EXISTS ownership_with_names"))
        
        # Create view that joins ownerships with game names
        create_view_sql = """
        CREATE VIEW ownership_with_names AS
        SELECT 
            o.id,
            o.steamid,
            o.appid,
            COALESCE(g.name, CONCAT('Unknown Game (', o.appid, ')')) as game_name,
            g.type as game_type,
            g.is_free,
            o.playtime_forever,
            ROUND(o.playtime_forever / 60.0, 1) as playtime_hours,
            o.created_at
        FROM ownerships o
        LEFT JOIN games g ON o.appid = g.appid
        ORDER BY o.playtime_forever DESC
        """
        
        session.execute(text(create_view_sql))
        session.commit()
        
        print("✅ Created 'ownership_with_names' view!")
        print("\nYou can now query it like:")
        print("SELECT * FROM ownership_with_names LIMIT 10;")
        
        # Test the view
        result = session.execute(text("SELECT * FROM ownership_with_names LIMIT 5"))
        rows = result.fetchall()
        
        print(f"\n=== Sample Data (Top 5 by Playtime) ===")
        print(f"{'Game Name':<40} {'Hours':<8} {'Minutes'}")
        print("-" * 60)
        
        for row in rows:
            game_name = row[3][:37] + "..." if len(row[3]) > 40 else row[3]
            hours = row[7] if row[7] else 0
            minutes = row[6] if row[6] else 0
            print(f"{game_name:<40} {hours:<8} {minutes}")

def main():
    create_ownership_view()

if __name__ == "__main__":
    main()