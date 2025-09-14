#!/usr/bin/env python3
"""Find Steam game IDs by searching game names"""

import sys
import os
import requests
import json
from typing import List, Dict

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def get_all_steam_apps() -> List[Dict]:
    """Fetch all Steam apps from the API"""
    print("Fetching all Steam apps... (this may take a moment)")
    url = "https://api.steampowered.com/ISteamApps/GetAppList/v2/"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()["applist"]["apps"]

def search_games(search_term: str, apps: List[Dict]) -> List[Dict]:
    """Search for games by name"""
    search_term = search_term.lower()
    matches = []
    
    for app in apps:
        if search_term in app["name"].lower():
            matches.append(app)
    
    return matches[:20]  # Limit to top 20 results

def main():
    search_term = input("Enter game name to search for: ").strip()
    
    if not search_term:
        print("Please enter a game name")
        return
    
    try:
        apps = get_all_steam_apps()
        matches = search_games(search_term, apps)
        
        if not matches:
            print(f"No games found matching '{search_term}'")
            return
        
        print(f"\nFound {len(matches)} games matching '{search_term}':")
        print("-" * 60)
        
        for app in matches:
            print(f"ID: {app['appid']:>8} | Name: {app['name']}")
        
        print("-" * 60)
        print("\nTo fetch data for these games, use option 2 in the main menu with:")
        app_ids = ",".join(str(app['appid']) for app in matches[:5])
        print(f"App IDs: {app_ids}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()