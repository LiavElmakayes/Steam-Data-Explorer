import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from steam_explorer.etl.pipeline import (
    transform_appdetails_to_games,
    transform_global_achievements,
    transform_owned_games,
)


def test_transform_appdetails_to_games_basic():
    appdetails = {
        "570": {"success": True, "data": {"name": "Dota 2", "type": "game", "is_free": True}},
        "bad": {"success": True, "data": {"name": "Bad"}},
        "730": {"success": False},
    }
    games = transform_appdetails_to_games(appdetails)
    assert any(g.appid == 570 and g.name == "Dota 2" for g in games)
    assert all(g.appid != 730 for g in games)


def test_transform_global_achievements_validation():
    resp = {
        "achievementpercentages": {
            "achievements": [
                {"name": "ach1", "percent": 50},
                {"name": "ach2", "percent": -1},
                {"name": None, "percent": 10},
            ]
        }
    }
    ach = transform_global_achievements(570, resp)
    names = [a.name for a in ach]
    assert "ach1" in names
    assert "ach2" not in names


def test_transform_owned_games_basic():
    resp = {"response": {"games": [{"appid": 570, "playtime_forever": 100}, {"appid": "bad"}]}}
    out = transform_owned_games("123", resp)
    assert any(o.appid == 570 and o.playtime_forever == 100 for o in out)
    assert all(o.appid != "bad" for o in out)
