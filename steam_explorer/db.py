from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session


class Base(DeclarativeBase):
    pass


def get_engine(database_url: str):
    return create_engine(database_url, future=True)


def get_sessionmaker(database_url: str):
    engine = get_engine(database_url)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False, future=True)


def get_session(database_url: str) -> Generator[Session, None, None]:
    SessionLocal = get_sessionmaker(database_url)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
