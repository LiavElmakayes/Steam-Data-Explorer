import argparse
from typing import List

from steam_explorer.config import get_settings
from steam_explorer.api.steam_client import SteamClient
from steam_explorer.db import get_sessionmaker
from steam_explorer.etl.pipeline import (
    transform_appdetails_to_games,
    transform_global_achievements,
    transform_owned_games,
    upsert_games,
    insert_ignore_conflicts,
)
from steam_explorer.logging_utils import get_logger, setup_logging


logger = get_logger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch data from Steam API and load into DB")
    parser.add_argument("--apps", type=str, default="", help="Comma-separated appids to fetch app details and global achievements")
    parser.add_argument("--owned", action="store_true", help="Fetch owned games for a steam user id")
    parser.add_argument("--steamid", type=str, default="", help="SteamID64; falls back to STEAM_USER_ID64 if empty")
    parser.add_argument("--rps", type=float, default=2.0, help="Requests per second limit (default 2.0)")
    parser.add_argument("--batch-size", type=int, default=50, help="Batch size for appdetails (default 50)")
    return parser.parse_args()


def main() -> None:
    setup_logging()
    args = parse_args()
    settings = get_settings()
    client = SteamClient(api_key=settings.steam_api_key, requests_per_second=args.rps)
    SessionLocal = get_sessionmaker(settings.database_url)

    steamid = args.steamid or (settings.steam_user_id64 or "")

    with SessionLocal.begin() as session:
        # Apps ETL
        appids: List[int] = []
        if args.apps:
            try:
                appids = [int(x.strip()) for x in args.apps.split(",") if x.strip()]
            except ValueError:
                logger.error("--apps must be a comma-separated list of integers")
                raise SystemExit(2)
        if appids:
            logger.info(f"Fetching details for {len(appids)} apps")
            appdetails = client.get_app_details(appids, batch_size=max(1, args.batch_size))
            games = transform_appdetails_to_games(appdetails)
            upserted = upsert_games(session, games)
            logger.info(f"Upserted {upserted} games")

            # Global achievements per app
            total_ach_rows = 0
            for appid in appids:
                ach_resp = client.get_global_achievements_for_app(appid)
                ach_rows = transform_global_achievements(appid, ach_resp)
                total_ach_rows += insert_ignore_conflicts(session, ach_rows)
            logger.info(f"Inserted up to {total_ach_rows} global achievement rows (duplicates ignored on commit)")

        # Owned games ETL
        if args.owned:
            if not steamid:
                logger.error("Provide --steamid or set STEAM_USER_ID64 in environment")
                raise SystemExit(2)
            logger.info(f"Fetching owned games for steamid={steamid}")
            owned_resp = client.get_owned_games(steamid)
            ownership_rows = transform_owned_games(steamid, owned_resp)
            inserted = insert_ignore_conflicts(session, ownership_rows)
            logger.info(f"Inserted up to {inserted} ownership rows (duplicates ignored on commit)")


if __name__ == "__main__":
    main()
