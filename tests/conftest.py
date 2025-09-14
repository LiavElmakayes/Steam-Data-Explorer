import os
import sys
import tempfile
import pytest
from sqlalchemy.orm import Session

# Add the project root to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from steam_explorer.config import Settings
from steam_explorer.db import get_engine, get_sessionmaker
from steam_explorer.api.steam_client import SteamClient


@pytest.fixture(scope="session")
def test_settings() -> Settings:
    # Use a temporary SQLite DB file per test session
    tmp_db = os.path.join(tempfile.gettempdir(), "steam_etl_test.db")
    return Settings(steam_api_key="test_key", database_url=f"sqlite:///{tmp_db}")


@pytest.fixture(scope="session")
def engine(test_settings):
    return get_engine(test_settings.database_url)


@pytest.fixture()
def session(test_settings) -> Session:
    SessionLocal = get_sessionmaker(test_settings.database_url)
    with SessionLocal.begin() as s:
        yield s


@pytest.fixture()
def steam_client(test_settings) -> SteamClient:
    # Use a slow RPS for tests to avoid flakiness if real calls are used
    return SteamClient(api_key=test_settings.steam_api_key, requests_per_second=1.0)
