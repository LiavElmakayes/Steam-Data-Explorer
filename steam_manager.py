#!/usr/bin/env python3
"""
Steam Data Explorer Manager
Main interface for managing your Steam data pipeline
"""

import sys
import os
import subprocess

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def run_tool(script_name, args=None):
    """Run a tool script with optional arguments"""
    try:
        cmd = [sys.executable, f"tools/{script_name}"]
        if args:
            cmd.extend(args)
        
        result = subprocess.run(cmd, cwd=project_root)
        return result.returncode == 0
    except Exception as e:
        print(f"Error running {script_name}: {e}")
        return False

def main_menu():
    """Display the main menu and handle user choices"""
    while True:
        print("\n" + "="*60)
        print("🎮 STEAM DATA EXPLORER MANAGER")
        print("="*60)
        print("📊 DATA MANAGEMENT")
        print("  1. Initialize Database")
        print("  2. Fetch Game Details (by App IDs)")
        print("  3. Fetch Your Owned Games")
        print("  4. Fetch All Missing Game Details")
        print()
        print("🔍 DATA EXPLORATION")
        print("  5. Database Explorer (Interactive)")
        print("  6. View Data Summary")
        print("  7. Find Game IDs by Name")
        print()
        print("🛠️  UTILITIES")
        print("  8. Test Database Connection")
        print("  9. Create Database Views")
        print(" 10. Add Game Names to Ownerships Table")
        print()
        print("📖 HELP & INFO")
        print(" 11. Show Project Structure")
        print(" 12. Show Configuration")
        print()
        print("  0. Exit")
        print("="*60)
        
        choice = input("Enter your choice (0-12): ").strip()
        
        if choice == "0":
            print("👋 Goodbye!")
            break
        elif choice == "1":
            print("🔧 Initializing database...")
            success = run_tool("init_db.py")
            if success:
                print("✅ Database initialized successfully!")
            else:
                print("❌ Database initialization failed!")
                
        elif choice == "2":
            app_ids = input("Enter comma-separated App IDs (e.g., 730,440,570): ").strip()
            if app_ids:
                print(f"📥 Fetching details for games: {app_ids}")
                success = run_tool("fetch_games.py", ["--apps", app_ids, "--batch-size", "1"])
                if success:
                    print("✅ Game details fetched successfully!")
                else:
                    print("❌ Failed to fetch game details!")
            else:
                print("❌ No App IDs provided!")
                
        elif choice == "3":
            print("📥 Fetching your owned games...")
            success = run_tool("fetch_games.py", ["--owned"])
            if success:
                print("✅ Owned games fetched successfully!")
            else:
                print("❌ Failed to fetch owned games!")
                
        elif choice == "4":
            print("📥 Fetching details for all missing games...")
            print("⏳ This may take several minutes due to rate limiting...")
            print("ℹ️  This will also automatically sync game names in your ownership records.")
            success = run_tool("fetch_all_owned_games.py")
            if success:
                print("✅ All game details fetched and game names synced successfully!")
            else:
                print("❌ Failed to fetch all game details!")
                
        elif choice == "5":
            print("🔍 Opening interactive database explorer...")
            run_tool("database_explorer.py")
            
        elif choice == "6":
            print("📊 Viewing data summary...")
            run_tool("view_data.py")
            
        elif choice == "7":
            print("🔍 Opening game ID finder...")
            run_tool("find_game_ids.py")
            
        elif choice == "8":
            print("🔌 Testing database connection...")
            success = run_tool("test_connection.py")
            if success:
                print("✅ Database connection successful!")
            else:
                print("❌ Database connection failed!")
                
        elif choice == "9":
            print("🗂️  Creating database views...")
            success = run_tool("create_ownership_view.py")
            if success:
                print("✅ Database views created successfully!")
            else:
                print("❌ Failed to create database views!")
                
        elif choice == "10":
            print("📝 Adding game names to ownerships table...")
            success = run_tool("add_game_names_to_ownerships.py")
            if success:
                print("✅ Game names added successfully!")
            else:
                print("❌ Failed to add game names!")
                
        elif choice == "11":
            show_project_structure()
            
        elif choice == "12":
            show_configuration()
            
        else:
            print("❌ Invalid choice! Please enter a number between 0-12.")
        
        if choice != "0":
            input("\nPress Enter to continue...")

def show_project_structure():
    """Display the project structure"""
    print("\n📁 PROJECT STRUCTURE")
    print("="*50)
    structure = """
steam_data_explorer/
├── steam_manager.py          # 👈 Main interface (you are here)
├── .env                      # Configuration file
├── requirements.txt          # Python dependencies
├── README.md                 # Documentation
├── steam.db                  # SQLite database (if using SQLite)
│
├── steam_explorer/           # Core application code
│   ├── __init__.py
│   ├── config.py            # Configuration management
│   ├── db.py                # Database connections
│   ├── models.py            # Data models
│   ├── logging_utils.py     # Logging utilities
│   ├── api/
│   │   └── steam_client.py  # Steam API client
│   └── etl/
│       └── pipeline.py      # Data transformation logic
│
├── tools/                   # Utility scripts
│   ├── init_db.py          # Initialize database
│   ├── fetch_games.py      # Fetch game data
│   ├── database_explorer.py # Interactive data browser
│   ├── find_game_ids.py    # Find Steam game IDs
│   └── ... (other utilities)
│
├── scripts/                 # Original scripts (legacy)
├── alembic/                 # Database migrations
└── tests/                   # Test suite
    """
    print(structure)

def show_configuration():
    """Display current configuration"""
    print("\n⚙️  CURRENT CONFIGURATION")
    print("="*50)
    
    try:
        from steam_explorer.config import get_settings
        settings = get_settings()
        
        print(f"Steam API Key: {'✅ Configured' if settings.steam_api_key else '❌ Missing'}")
        print(f"Database URL: {settings.database_url}")
        print(f"Steam User ID: {'✅ Configured' if settings.steam_user_id64 else '❌ Not set'}")
        
        # Check if database exists
        if "sqlite" in settings.database_url.lower():
            db_file = settings.database_url.split("///")[-1]
            db_exists = os.path.exists(db_file)
            print(f"Database File: {'✅ Exists' if db_exists else '❌ Not found'}")
        else:
            print("Database Type: MySQL/PostgreSQL")
            
    except Exception as e:
        print(f"❌ Error reading configuration: {e}")
        print("\nMake sure your .env file is properly configured!")

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)