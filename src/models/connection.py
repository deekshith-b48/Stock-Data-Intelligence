"""
Database connection and session management for Stock Data Intelligence Dashboard.

This module provides:
- Database engine creation with connection pooling
- Session management with context managers
- Retry logic with exponential backoff
- Support for both PostgreSQL and SQLite
"""

import os
import time
import logging
from typing import Generator
from contextlib import contextmanager

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import OperationalError, DBAPIError
from sqlalchemy.pool import QueuePool, StaticPool

from .database import Base

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """
    Manages database connections with pooling and retry logic.
    
    Supports both PostgreSQL (production) and SQLite (development) via
    DATABASE_URL environment variable.
    """
    
    def __init__(self, database_url: str = None, pool_size: int = 10, max_overflow: int = 20):
        """
        Initialize database connection.
        
        Args:
            database_url: Database connection string. If None, reads from DATABASE_URL env var.
            pool_size: Number of connections to maintain in the pool (default: 10)
            max_overflow: Maximum overflow connections beyond pool_size (default: 20)
        """
        self.database_url = database_url or os.getenv('DATABASE_URL', 'sqlite:///./stock_dashboard.db')
        self.pool_size = pool_size
        self.max_overflow = max_overflow
        self.engine = None
        self.SessionLocal = None
        
        self._create_engine()
    
    def _create_engine(self):
        """Create SQLAlchemy engine with appropriate configuration."""
        is_sqlite = self.database_url.startswith('sqlite')
        
        if is_sqlite:
            # SQLite configuration: use StaticPool for in-memory or single-threaded access
            logger.info("Configuring SQLite database connection")
            self.engine = create_engine(
                self.database_url,
                connect_args={"check_same_thread": False},
                poolclass=StaticPool,
                echo=os.getenv('DEBUG', 'false').lower() == 'true'
            )
        else:
            # PostgreSQL configuration: use QueuePool with connection pooling
            logger.info(f"Configuring PostgreSQL database connection with pool_size={self.pool_size}")
            self.engine = create_engine(
                self.database_url,
                poolclass=QueuePool,
                pool_size=self.pool_size,
                max_overflow=self.max_overflow,
                pool_pre_ping=True,  # Verify connections before using
                pool_recycle=3600,   # Recycle connections after 1 hour
                echo=os.getenv('DEBUG', 'false').lower() == 'true'
            )
        
        # Create session factory
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Add connection event listeners for logging
        @event.listens_for(self.engine, "connect")
        def receive_connect(dbapi_conn, connection_record):
            logger.debug("Database connection established")
        
        @event.listens_for(self.engine, "close")
        def receive_close(dbapi_conn, connection_record):
            logger.debug("Database connection closed")
    
    def create_tables(self):
        """Create all tables defined in the ORM models."""
        logger.info("Creating database tables")
        Base.metadata.create_all(bind=self.engine)
    
    def drop_tables(self):
        """Drop all tables (use with caution!)."""
        logger.warning("Dropping all database tables")
        Base.metadata.drop_all(bind=self.engine)
    
    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """
        Context manager for database sessions.
        
        Yields:
            Session: SQLAlchemy session
            
        Example:
            with db.get_session() as session:
                companies = session.query(Company).all()
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Session error: {e}", exc_info=True)
            raise
        finally:
            session.close()
    
    def get_session_with_retry(self, max_attempts: int = 3) -> Session:
        """
        Get a database session with retry logic and exponential backoff.
        
        Args:
            max_attempts: Maximum number of connection attempts (default: 3)
            
        Returns:
            Session: SQLAlchemy session
            
        Raises:
            OperationalError: If all connection attempts fail
        """
        attempt = 0
        last_exception = None
        
        while attempt < max_attempts:
            try:
                session = self.SessionLocal()
                # Test the connection
                session.execute(text("SELECT 1"))
                logger.info(f"Database connection successful on attempt {attempt + 1}")
                return session
            except (OperationalError, DBAPIError) as e:
                last_exception = e
                attempt += 1
                if attempt < max_attempts:
                    # Exponential backoff: 1s, 2s, 4s
                    wait_time = 2 ** (attempt - 1)
                    logger.warning(
                        f"Database connection attempt {attempt} failed: {e}. "
                        f"Retrying in {wait_time} seconds..."
                    )
                    time.sleep(wait_time)
                else:
                    logger.error(f"Database connection failed after {max_attempts} attempts")
        
        raise OperationalError(
            f"Failed to connect to database after {max_attempts} attempts",
            params=None,
            orig=last_exception
        )
    
    @contextmanager
    def get_session_with_retry_context(self, max_attempts: int = 3) -> Generator[Session, None, None]:
        """
        Context manager for database sessions with retry logic.
        
        Args:
            max_attempts: Maximum number of connection attempts (default: 3)
            
        Yields:
            Session: SQLAlchemy session
            
        Example:
            with db.get_session_with_retry_context() as session:
                companies = session.query(Company).all()
        """
        session = self.get_session_with_retry(max_attempts=max_attempts)
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Session error: {e}", exc_info=True)
            raise
        finally:
            session.close()
    
    def close(self):
        """Close the database engine and all connections."""
        if self.engine:
            logger.info("Closing database engine")
            self.engine.dispose()


# Global database instance
_db_instance = None


def get_database() -> DatabaseConnection:
    """
    Get or create the global database instance.
    
    Returns:
        DatabaseConnection: Global database connection instance
    """
    global _db_instance
    if _db_instance is None:
        pool_size = int(os.getenv('DB_POOL_SIZE', '10'))
        max_overflow = int(os.getenv('DB_MAX_OVERFLOW', '20'))
        _db_instance = DatabaseConnection(pool_size=pool_size, max_overflow=max_overflow)
    return _db_instance


def init_database():
    """Initialize the database by creating all tables."""
    db = get_database()
    db.create_tables()
    logger.info("Database initialized successfully")
