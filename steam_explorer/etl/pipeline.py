from __future__ import annotations
from typing import Iterable, List
from sqlalchemy.orm import Session
from ..models import Game, AchievementGlobal, Ownership
from ..logging_utils import get_logger


logger = get_logger(__name__)


def transform_appdetails_to_games(appdetails: dict) -> List[Game]:
    games: List[Game] = []
    for appid_str, payload in appdetails.items():
        try:
            appid = int(appid_str)
        except ValueError:
            logger.warning(f"Skipping invalid appid key: {appid_str}")
            continue
        if not isinstance(payload, dict) or not payload.get("success"):
            logger.debug(f"No data/success=false for appid={appid}")
            continue
        data = payload.get("data") or {}
        name = (data.get("name") or f"App {appid}").strip()
        if not name:
            logger.warning(f"Skipping appid={appid} due to empty name")
            continue
        game_type = data.get("type")
        is_free = data.get("is_free")
        games.append(Game(appid=appid, name=name[:255], type=(game_type[:64] if game_type else None), is_free=bool(is_free) if is_free is not None else None))
    logger.info(f"Transformed {len(games)} games from appdetails")
    return games


def transform_global_achievements(appid: int, response: dict) -> List[AchievementGlobal]:
    achievements: List[AchievementGlobal] = []
    data = (response or {}).get("achievementpercentages", {}).get("achievements", [])
    for item in data:
        name = item.get("name")
        percent = item.get("percent")
        if name is None or percent is None:
            logger.debug("Skipping achievement with missing name/percent")
            continue
        try:
            p = float(percent)
            if p < 0 or p > 100:
                logger.debug(f"Skipping achievement percent out of range: {p}")
                continue
        except (TypeError, ValueError):
            logger.debug(f"Skipping achievement due to non-numeric percent: {percent}")
            continue
        achievements.append(AchievementGlobal(appid=appid, name=str(name)[:255], percent=p))
    logger.info(f"Transformed {len(achievements)} global achievements for appid={appid}")
    return achievements


def transform_owned_games(steamid: str, response: dict) -> List[Ownership]:
    ownerships: List[Ownership] = []
    games = (response or {}).get("response", {}).get("games", [])
    for g in games:
        appid = g.get("appid")
        if appid is None:
            logger.debug("Skipping owned game with missing appid")
            continue
        playtime = g.get("playtime_forever")
        game_name = g.get("name")  # Steam API includes game name in owned games response
        try:
            appid_int = int(appid)
        except (TypeError, ValueError):
            logger.debug(f"Skipping owned game with non-integer appid: {appid}")
            continue
        pt = None
        if playtime is not None:
            try:
                pt = int(playtime)
                if pt < 0:
                    logger.debug(f"Clamping negative playtime to 0 for appid={appid_int}")
                    pt = 0
            except (TypeError, ValueError):
                logger.debug(f"Ignoring non-integer playtime for appid={appid_int}")
        
        # Use game name from API if available, otherwise leave as None
        name_to_use = game_name[:255] if game_name else None
        ownerships.append(Ownership(steamid=steamid, appid=appid_int, game_name=name_to_use, playtime_forever=pt))
    logger.info(f"Transformed {len(ownerships)} ownership rows for steamid={steamid}")
    return ownerships


def upsert_games(session: Session, games: Iterable[Game]) -> int:
    count = 0
    for game in games:
        if not game.appid or not game.name:
            logger.debug(f"Skipping invalid game row: {game}")
            continue
        existing = session.get(Game, game.appid)
        if existing:
            existing.name = game.name
            existing.type = game.type
            existing.is_free = game.is_free
        else:
            session.add(game)
        count += 1
    logger.info(f"Upserted {count} games")
    return count


def upsert_achievements(session: Session, achievements: Iterable[AchievementGlobal]) -> int:
    """Upsert achievements, updating existing ones or inserting new ones"""
    count = 0
    for achievement in achievements:
        if not achievement.appid or not achievement.name:
            logger.debug(f"Skipping invalid achievement row: {achievement}")
            continue
        
        # Check if achievement already exists
        existing = session.query(AchievementGlobal).filter(
            AchievementGlobal.appid == achievement.appid,
            AchievementGlobal.name == achievement.name
        ).first()
        
        if existing:
            # Update existing achievement
            existing.percent = achievement.percent
            logger.debug(f"Updated achievement {achievement.name} for appid {achievement.appid}")
        else:
            # Insert new achievement
            session.add(achievement)
            logger.debug(f"Added new achievement {achievement.name} for appid {achievement.appid}")
        count += 1
    
    logger.info(f"Upserted {count} achievements")
    return count

def upsert_ownerships(session: Session, ownerships: Iterable[Ownership]) -> int:
    """Upsert ownerships, updating existing ones or inserting new ones"""
    count = 0
    for ownership in ownerships:
        if not ownership.steamid or not ownership.appid:
            logger.debug(f"Skipping invalid ownership row: {ownership}")
            continue
        
        # Check if ownership already exists
        existing = session.query(Ownership).filter(
            Ownership.steamid == ownership.steamid,
            Ownership.appid == ownership.appid
        ).first()
        
        if existing:
            # Update existing ownership
            existing.playtime_forever = ownership.playtime_forever
            existing.game_name = ownership.game_name
            logger.debug(f"Updated ownership for steamid {ownership.steamid}, appid {ownership.appid}")
        else:
            # Insert new ownership
            session.add(ownership)
            logger.debug(f"Added new ownership for steamid {ownership.steamid}, appid {ownership.appid}")
        count += 1
    
    logger.info(f"Upserted {count} ownerships")
    return count

def insert_ignore_conflicts(session: Session, rows: Iterable[object]) -> int:
    """Legacy function - use specific upsert functions instead"""
    count = 0
    for row in rows:
        try:
            session.add(row)
            count += 1
        except Exception as exc:
            logger.warning(f"Deferred insert error until commit: {exc}")
            pass
    logger.info(f"Queued up to {count} rows for insert")
    return count
