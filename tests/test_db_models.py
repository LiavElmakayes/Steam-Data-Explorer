import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from steam_explorer.models import Base, Game
from steam_explorer.db import get_engine


def test_create_tables_and_insert(engine):
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    # Simple insertion check via SQLAlchemy Core
    with engine.begin() as conn:
        conn.execute(Game.__table__.insert().values(appid=1, name="Test Game"))
        res = conn.execute(Game.__table__.select().where(Game.__table__.c.appid == 1)).fetchone()
        assert res is not None
        assert res._mapping["name"] == "Test Game"
