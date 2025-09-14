#!/usr/bin/env python3
"""Interactive database explorer for Steam data"""

import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from steam_explorer.config import get_settings
from steam_explorer.db import get_sessionmaker
from steam_explorer.models import Game, Ownership, AchievementGlobal
from sqlalchemy import func, text

def main():
    settings = get_settings()
    SessionLocal = get_sessionmaker(settings.database_url)
    
    with SessionLocal() as session:
        while True:
            print("\n" + "="*50)
            print("Steam Database Explorer")
            print("="*50)
            print("1. Database Summary")
            print("2. View Your Owned Games")
            print("3. View Games with Details")
            print("4. View Achievements")
            print("5. Top Games by Playtime")
            print("6. Search Games")
            print("7. Raw SQL Query")
            print("0. Exit")
            
            choice = input("\nEnter your choice (0-7): ").strip()
            
            if choice == "0":
                print("Goodbye!")
                break
            elif choice == "1":
                show_summary(session)
            elif choice == "2":
                show_owned_games(session)
            elif choice == "3":
                show_games(session)
            elif choice == "4":
                show_achievements(session)
            elif choice == "5":
                show_top_playtime(session)
            elif choice == "6":
                search_games(session)
            elif choice == "7":
                raw_sql(session)
            else:
                print("Invalid choice!")

def show_summary(session):
    print("\n=== Database Summary ===")
    game_count = session.query(func.count(Game.appid)).scalar()
    ownership_count = session.query(func.count(Ownership.id)).scalar()
    achievement_count = session.query(func.count(AchievementGlobal.id)).scalar()
    
    print(f"Games with details: {game_count}")
    print(f"Your owned games: {ownership_count}")
    print(f"Achievement records: {achievement_count}")

def show_owned_games(session):
    print("\n=== Your Owned Games ===")
    ownerships = session.query(Ownership).order_by(Ownership.playtime_forever.desc().nullslast()).limit(20).all()
    
    if not ownerships:
        print("No owned games found!")
        return
    
    print(f"{'Game Name':<40} {'App ID':<10} {'Hours':<8} {'Minutes'}")
    print("-" * 70)
    
    for ownership in ownerships:
        game_name = ownership.game_name or f"Unknown ({ownership.appid})"
        game_name = game_name[:37] + "..." if len(game_name) > 40 else game_name
        playtime_min = ownership.playtime_forever or 0
        playtime_hrs = round(playtime_min / 60, 1) if playtime_min > 0 else 0
        print(f"{game_name:<40} {ownership.appid:<10} {playtime_hrs:<8} {playtime_min}")

def show_games(session):
    print("\n=== Games with Details ===")
    games = session.query(Game).order_by(Game.name).limit(20).all()
    
    if not games:
        print("No game details found! Use option 2 in main menu to fetch game data.")
        return
    
    print(f"{'App ID':<10} {'Name':<40} {'Type':<15} {'Free?'}")
    print("-" * 80)
    
    for game in games:
        free_status = "Yes" if game.is_free else "No" if game.is_free is not None else "Unknown"
        name = game.name[:37] + "..." if len(game.name) > 40 else game.name
        game_type = game.type or "Unknown"
        print(f"{game.appid:<10} {name:<40} {game_type:<15} {free_status}")

def show_achievements(session):
    print("\n=== Achievement Data ===")
    achievements = session.query(AchievementGlobal).order_by(AchievementGlobal.percent.desc()).limit(20).all()
    
    if not achievements:
        print("No achievement data found!")
        return
    
    print(f"{'App ID':<10} {'Achievement Name':<40} {'Completion %'}")
    print("-" * 65)
    
    for ach in achievements:
        name = ach.name[:37] + "..." if len(ach.name) > 40 else ach.name
        print(f"{ach.appid:<10} {name:<40} {ach.percent:.1f}%")

def show_top_playtime(session):
    print("\n=== Your Top Games by Playtime ===")
    ownerships = session.query(Ownership).filter(
        Ownership.playtime_forever > 0
    ).order_by(Ownership.playtime_forever.desc()).limit(10).all()
    
    if not ownerships:
        print("No playtime data found!")
        return
    
    print(f"{'Game Name':<40} {'Hours':<10} {'Minutes'}")
    print("-" * 60)
    
    for ownership in ownerships:
        name = ownership.game_name or f"Unknown Game ({ownership.appid})"
        name = name[:37] + "..." if len(name) > 40 else name
        hours = round(ownership.playtime_forever / 60, 1)
        print(f"{name:<40} {hours:<10} {ownership.playtime_forever}")

def search_games(session):
    search_term = input("\nEnter game name to search: ").strip()
    if not search_term:
        return
    
    games = session.query(Game).filter(Game.name.ilike(f"%{search_term}%")).limit(10).all()
    
    if not games:
        print(f"No games found matching '{search_term}'")
        return
    
    print(f"\nGames matching '{search_term}':")
    print(f"{'App ID':<10} {'Name':<50}")
    print("-" * 60)
    
    for game in games:
        print(f"{game.appid:<10} {game.name}")

def raw_sql(session):
    print("\nEnter SQL query (or 'back' to return):")
    query = input("SQL> ").strip()
    
    if query.lower() == 'back':
        return
    
    try:
        result = session.execute(text(query))
        rows = result.fetchall()
        
        if rows:
            # Print column headers if available
            if hasattr(result, 'keys'):
                headers = result.keys()
                print(" | ".join(str(h) for h in headers))
                print("-" * (len(" | ".join(str(h) for h in headers))))
            
            # Print rows
            for row in rows[:50]:  # Limit to 50 rows
                print(" | ".join(str(col) for col in row))
            
            if len(rows) > 50:
                print(f"... and {len(rows) - 50} more rows")
        else:
            print("Query executed successfully (no results)")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()