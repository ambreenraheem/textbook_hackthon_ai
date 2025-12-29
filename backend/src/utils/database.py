"""
Database utilities for session management and persistence.

Provides database session context managers and helper functions.
"""
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool

from src.config.settings import get_settings
from src.utils.app_logging import get_logger

logger = get_logger(__name__)


# Global engine and session factory
_engine = None
_SessionLocal = None


def init_database():
    """
    Initialize database engine and session factory.

    Should be called during application startup.
    """
    global _engine, _SessionLocal

    settings = get_settings()

    logger.info("Initializing database connection")

    # Create engine with connection pooling
    # For Neon Serverless Postgres, use NullPool to avoid connection pooling issues
    _engine = create_engine(
        settings.database_url,
        poolclass=NullPool,  # Serverless-friendly: no connection pooling
        echo=False,  # Set to True for SQL query logging
        future=True
    )

    # Create session factory
    _SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=_engine,
        expire_on_commit=False
    )

    logger.info("Database initialized successfully")


def get_db_engine():
    """
    Get the global database engine.

    Returns:
        SQLAlchemy engine
    """
    global _engine

    if _engine is None:
        init_database()

    return _engine


def get_session_factory():
    """
    Get the global session factory.

    Returns:
        SQLAlchemy session factory
    """
    global _SessionLocal

    if _SessionLocal is None:
        init_database()

    return _SessionLocal


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """
    Context manager for database sessions.

    Usage:
        with get_db_session() as session:
            session.query(...)
            session.commit()

    Yields:
        SQLAlchemy session
    """
    SessionLocal = get_session_factory()
    session = SessionLocal()

    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database session error: {e}", exc_info=True)
        raise
    finally:
        session.close()


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency for database sessions.

    Usage:
        @app.get("/")
        def endpoint(db: Session = Depends(get_db)):
            db.query(...)

    Yields:
        SQLAlchemy session
    """
    SessionLocal = get_session_factory()
    db = SessionLocal()

    try:
        yield db
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {e}", exc_info=True)
        raise
    finally:
        db.close()


def create_tables():
    """
    Create all database tables.

    Should be called during application setup if tables don't exist.
    """
    from src.models.conversation import Base

    engine = get_db_engine()

    logger.info("Creating database tables")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")


def check_database_connection() -> bool:
    """
    Check if database connection is working.

    Returns:
        True if connection successful, False otherwise
    """
    try:
        engine = get_db_engine()
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"Database connection check failed: {e}")
        return False
