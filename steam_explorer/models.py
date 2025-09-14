from __future__ import annotations
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, Float, Boolean, DateTime, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from .db import Base


class Game(Base):
    __tablename__ = "games"

    appid: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    is_free: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class AchievementGlobal(Base):
    __tablename__ = "achievements_global"
    __table_args__ = (
        UniqueConstraint("appid", "name", name="uq_achievements_global_appid_name"),
        Index("ix_achievements_global_appid", "appid"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    appid: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    percent: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class Ownership(Base):
    __tablename__ = "ownerships"
    __table_args__ = (
        Index("ix_ownerships_steamid", "steamid"),
        Index("ix_ownerships_appid", "appid"),
        UniqueConstraint("steamid", "appid", name="uq_ownerships_steamid_appid"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    steamid: Mapped[str] = mapped_column(String(32), nullable=False)
    appid: Mapped[int] = mapped_column(Integer, nullable=False)
    playtime_forever: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
