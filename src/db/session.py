"""
Database connection and session management.
Provides engine creation, session factories, and database initialization.
"""

from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from config.settings import DATABASE_URL
from src.db.base import Base

# Create engine. For SQLite, connect_args={"check_same_thread": False} allows usage in GUI threads.
def get_engine(db_url: str = DATABASE_URL):
    connect_args = {}
    if db_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
    return create_engine(db_url, echo=False, connect_args=connect_args)

# Engine and sessionmaker singleton instances
engine = get_engine()
SessionFactory = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db(target_engine=None):
    """
    Creates all tables in the database if they do not already exist.
    """
    eng = target_engine or engine
    # Import all models to ensure they are registered with Base.metadata
    from src import models  # noqa: F401
    Base.metadata.create_all(bind=eng)

def get_session(target_factory=None) -> Session:
    """
    Returns a new SQLAlchemy Session. Caller is responsible for closing it or using a context manager.
    """
    factory = target_factory or SessionFactory
    return factory()

def session_scope(target_factory=None) -> Generator[Session, None, None]:
    """
    Context manager for transactional scope around a series of operations.
    """
    session = get_session(target_factory)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
