#!/usr/bin/env python3
"""Fetch details for all owned games"""

import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from steam_explorer.config import get_settings
from steam_explorer.db import get_sessionmaker
from steam_explorer.models import Ownership, Game
from steam_explorer.api.steam_client import SteamClient
from steam_explorer.etl.pipeline import transform_appdetails_to_games, upsert_games

def fetch_missing_game_details():
    settings = get_settings()
    SessionLocal = get_sessionmaker(settings.database_url)
    
    with SessionLocal() as session:
        # Find all owned games that don't have details in the games table
        owned_appids = session.query(Ownership.appid).distinct().all()
        existing_game_appids = session.query(Game.appid).all()
        
        owned_set = {appid[0] for appid in owned_appids}
        existing_set = {appid[0] for appid in existing_game_appids}
        
        missing_appids = list(owned_set - existing_set)
        
        print(f"You own {len(owned_set)} games")
        print(f"You have details for {len(existing_set)} games")
        print(f"Missing details for {len(missing_appids)} games")
        
        if not missing_appids:
            print("✅ All your owned games already have details!")
            return
        
        print(f"\nFetching details for {len(missing_appids)} games...")
        print("This will take a few minutes due to rate limiting...")
        
        # Fetch details in small batches
        client = SteamClient(api_key=settings.steam_api_key, requests_per_second=1.5)
        
        batch_size = 10
        total_fetched = 0
        
        for i in range(0, len(missing_appids), batch_size):
            batch = missing_appids[i:i+batch_size]
            print(f"\nFetching batch {i//batch_size + 1}/{(len(missing_appids) + batch_size - 1)//batch_size}")
            print(f"App IDs: {batch}")
            
            try:
                appdetails = client.get_app_details(batch, batch_size=1)  # Fetch one at a time
                games = transform_appdetails_to_games(appdetails)
                
                if games:
                    with SessionLocal.begin() as batch_session:
                        upserted = upsert_games(batch_session, games)
                        total_fetched += upserted
                        print(f"✅ Added {upserted} games to database")
                
            except Exception as e:
                print(f"❌ Error fetching batch: {e}")
                continue
        
        print(f"\n🎉 Finished! Fetched details for {total_fetched} games")
        
        # Now update ownership records with game names
        print("\n🔄 Updating ownership records with game names...")
        update_ownership_names()

def update_ownership_names():
    settings = get_settings()
    SessionLocal = get_sessionmaker(settings.database_url)
    
    with SessionLocal.begin() as session:
        # Update ownerships that don't have game names or have "Unknown Game"
        ownerships = session.query(Ownership).filter(
            (Ownership.game_name.is_(None)) | 
            (Ownership.game_name == '') |
            (Ownership.game_name.like('Unknown Game%'))
        ).all()
        
        updated_count = 0
        for ownership in ownerships:
            game = session.query(Game).filter(Game.appid == ownership.appid).first()
            
            if game:
                ownership.game_name = game.name
                updated_count += 1
            else:
                ownership.game_name = f"Unknown Game ({ownership.appid})"
        
        print(f"✅ Updated {updated_count} ownership records with game names")

def main():
    fetch_missing_game_details()

if __name__ == "__main__":
    main()