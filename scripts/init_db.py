from steam_explorer.config import get_settings
from steam_explorer.db import get_engine
from steam_explorer.models import Base
from steam_explorer.logging_utils import get_logger, setup_logging


logger = get_logger(__name__)


def main() -> None:
    setup_logging()
    settings = get_settings()
    logger.info("Initializing database schema...")
    engine = get_engine(settings.database_url)
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized.")


if __name__ == "__main__":
    main()
