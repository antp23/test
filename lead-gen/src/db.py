"""Database engine and session management."""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from src.config import get_settings


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""
    pass


def get_engine(echo: bool = False):
    """Create SQLAlchemy engine from settings."""
    settings = get_settings()
    return create_engine(settings.database_url, echo=echo)


def get_session_factory(echo: bool = False) -> sessionmaker[Session]:
    """Create a session factory."""
    engine = get_engine(echo=echo)
    return sessionmaker(bind=engine)


def init_db():
    """Create all tables (for development use)."""
    engine = get_engine()
    Base.metadata.create_all(engine)
