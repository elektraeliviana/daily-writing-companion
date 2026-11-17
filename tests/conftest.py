"""
Pytest configuration and shared fixtures.
Uses in-memory SQLite for instantaneous, isolated tests.
"""

import sys
from pathlib import Path
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.db.base import Base
from src import models  # noqa: F401


@pytest.fixture(scope="function")
def in_memory_engine():
    """Creates a fresh in-memory SQLite engine for each test function."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(in_memory_engine):
    """Provides a fresh isolated database session."""
    session_local = sessionmaker(autocommit=False, autoflush=False, bind=in_memory_engine)
    session = session_local()
    try:
        yield session
    finally:
        session.close()
