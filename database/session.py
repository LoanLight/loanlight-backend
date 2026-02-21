from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    future=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    future=True,
)


def db_session() -> Session:
    """
    FastAPI dependency that provides a SQLAlchemy Session.
    """
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()