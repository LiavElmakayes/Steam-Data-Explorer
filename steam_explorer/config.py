import os
from dataclasses import dataclass
from typing import Optional

try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    # dotenv is optional at runtime
    pass


@dataclass
class Settings:
    steam_api_key: str
    database_url: str = "sqlite:///steam.db"
    steam_user_id64: Optional[str] = None


_settings: Optional[Settings] = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        steam_api_key = os.getenv("STEAM_API_KEY", "").strip()
        if not steam_api_key:
            raise RuntimeError("STEAM_API_KEY is required. Set it in environment or .env.")
        database_url = os.getenv("DATABASE_URL", "sqlite:///steam.db").strip()
        steam_user_id64 = os.getenv("STEAM_USER_ID64")
        _settings = Settings(
            steam_api_key=steam_api_key,
            database_url=database_url,
            steam_user_id64=steam_user_id64.strip() if steam_user_id64 else None,
        )
    return _settings
