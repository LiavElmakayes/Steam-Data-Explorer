#!/usr/bin/env python3
"""View data in the Steam database"""

import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from steam_explorer.config import get_settings
from steam_explorer.db import get_sessionmaker
from steam_explorer.models import Game, Ownership, AchievementGlobal
from sqlalchemy import func

def main():
    settings = get_settings()
    SessionLocal = get_sessionmaker(settings.database_url)
    
    with SessionLocal() as session:
        print("\n" + "="*70)
        print("🎮 STEAM DATA SUMMARY")
        print("="*70)
        
        # Count records in each table
        game_count = session.query(func.count(Game.appid)).scalar()
        ownership_count = session.query(func.count(Ownership.id)).scalar()
        achievement_count = session.query(func.count(AchievementGlobal.id)).scalar()
        
        # Games with names vs unknown
        games_with_names = session.query(func.count(Ownership.id)).filter(
            Ownership.game_name.is_not(None),
            ~Ownership.game_name.like('Unknown Game%')
        ).scalar()
        games_without_names = ownership_count - games_with_names
        
        print(f"📊 DATABASE OVERVIEW:")
        print(f"   • Total games you own: {ownership_count}")
        print(f"   • Games with details: {game_count}")
        print(f"   • Games with names: {games_with_names}")
        print(f"   • Games needing details: {games_without_names}")
        print(f"   • Achievement records: {achievement_count}")
        
        if games_without_names > 0:
            print(f"\n⚠️  You have {games_without_names} games without details.")
            print("   Use option 4 in the main menu to fetch missing game details.")
        
        if ownership_count > 0:
            print(f"\n🏆 YOUR TOP GAMES BY PLAYTIME:")
            print("-" * 70)
            
            # Get games with playtime first
            ownerships = session.query(Ownership).filter(
                Ownership.playtime_forever.is_not(None),
                Ownership.playtime_forever > 0
            ).order_by(Ownership.playtime_forever.desc()).limit(10).all()
            
            if ownerships:
                print(f"{'Rank':<4} {'Game Name':<35} {'Hours':<8} {'Total Minutes'}")
                print("-" * 70)
                
                for i, ownership in enumerate(ownerships, 1):
                    game_name = ownership.game_name or f"Unknown ({ownership.appid})"
                    game_name = game_name[:32] + "..." if len(game_name) > 35 else game_name
                    hours = round(ownership.playtime_forever / 60, 1)
                    minutes = ownership.playtime_forever
                    print(f"{i:<4} {game_name:<35} {hours:<8} {minutes:,}")
            else:
                print("No games with recorded playtime found.")
                
            # Show total playtime
            total_minutes = session.query(func.sum(Ownership.playtime_forever)).filter(
                Ownership.playtime_forever.is_not(None)
            ).scalar() or 0
            total_hours = round(total_minutes / 60, 1)
            
            print("-" * 70)
            print(f"🎯 TOTAL PLAYTIME: {total_hours:,} hours ({total_minutes:,} minutes)")
        
        if game_count > 0:
            print(f"\n📚 SAMPLE GAMES IN DATABASE:")
            print("-" * 70)
            games = session.query(Game).limit(5).all()
            for game in games:
                game_type = game.type or "Unknown"
                free_status = "Free" if game.is_free else "Paid" if game.is_free is not None else "Unknown"
                print(f"   • {game.name} (ID: {game.appid}) - {game_type}, {free_status}")
            
            if game_count > 5:
                print(f"   ... and {game_count - 5} more games")
        
        print("\n" + "="*70)
        print("💡 TIP: Use option 5 (Database Explorer) for detailed interactive browsing!")
        print("="*70)

if __name__ == "__main__":
    main()