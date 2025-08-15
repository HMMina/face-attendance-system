"""
Database connection and session management - Optimized
"""
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# Create database engine with optimized settings
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=300,    # Recreate connections every 5 minutes
    echo=settings.DEBUG,  # Log SQL queries in debug mode
    connect_args={
        "check_same_thread": False,  # For SQLite compatibility
        "pool_timeout": 20,
        "pool_recycle": -1,
    } if "sqlite" in settings.DATABASE_URL else {
        "pool_timeout": 20,
    }
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Create metadata with naming convention for better migrations
metadata = MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s"
    }
)

# Create base class for models
Base = declarative_base(metadata=metadata)


# Dependency to get database session
def get_db() -> Session:
    """
    Database session dependency for FastAPI
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


# Database initialization
def init_db() -> None:
    """
    Initialize database tables
    """
    try:
        # Import all models to ensure they are registered
        from app.models import employee, device, attendance, network_log  # noqa
        
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


# Database health check
def check_db_connection() -> bool:
    """
    Check if database connection is healthy
    """
    try:
        db = SessionLocal()
        # Simple query to test connection
        db.execute("SELECT 1")
        db.close()
        return True
    except Exception as e:
        logger.error(f"Database connection check failed: {e}")
        return False


# Database cleanup
def close_db_connections() -> None:
    """
    Close all database connections
    """
    try:
        engine.dispose()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error closing database connections: {e}")
