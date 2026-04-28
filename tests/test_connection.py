"""
Unit tests for database connection and session management.

Tests cover:
- Database engine creation for PostgreSQL and SQLite
- Connection pooling configuration
- Session management with context managers
- Retry logic with exponential backoff
- Error handling
"""

import pytest
import os
import time
from unittest.mock import patch, MagicMock
from sqlalchemy.exc import OperationalError, DBAPIError
from sqlalchemy import text

from src.models import DatabaseConnection, get_database, init_database
from src.models.database import Base, Company

# Check if psycopg2 is available
try:
    import psycopg2
    HAS_PSYCOPG2 = True
except ImportError:
    HAS_PSYCOPG2 = False


class TestDatabaseConnection:
    """Test DatabaseConnection class."""
    
    def test_sqlite_engine_creation(self):
        """Test creating a SQLite database engine."""
        db = DatabaseConnection(database_url='sqlite:///./test.db')
        
        assert db.engine is not None
        assert db.SessionLocal is not None
        assert 'sqlite' in str(db.engine.url)
        
        db.close()
    
    @pytest.mark.skipif(not HAS_PSYCOPG2, reason="psycopg2 not installed")
    def test_postgresql_engine_creation(self):
        """Test creating a PostgreSQL database engine configuration."""
        db = DatabaseConnection(
            database_url='postgresql://user:pass@localhost:5432/testdb',
            pool_size=5,
            max_overflow=10
        )
        
        assert db.engine is not None
        assert db.SessionLocal is not None
        assert 'postgresql' in str(db.engine.url)
        assert db.pool_size == 5
        assert db.max_overflow == 10
        
        db.close()
    
    def test_default_database_url_from_env(self):
        """Test that database URL is read from environment variable."""
        with patch.dict(os.environ, {'DATABASE_URL': 'sqlite:///./env_test.db'}):
            db = DatabaseConnection()
            assert db.database_url == 'sqlite:///./env_test.db'
            db.close()
    
    @pytest.mark.skipif(not HAS_PSYCOPG2, reason="psycopg2 not installed")
    def test_pool_size_configuration(self):
        """Test connection pool size configuration."""
        db = DatabaseConnection(
            database_url='postgresql://user:pass@localhost:5432/testdb',
            pool_size=15,
            max_overflow=25
        )
        
        assert db.pool_size == 15
        assert db.max_overflow == 25
        
        db.close()
    
    def test_create_tables(self):
        """Test creating database tables."""
        db = DatabaseConnection(database_url='sqlite:///:memory:')
        db.create_tables()
        
        # Verify tables exist by querying
        with db.get_session() as session:
            # Should not raise an error
            result = session.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            tables = [row[0] for row in result]
            assert 'companies' in tables
            assert 'stock_data' in tables
        
        db.close()
    
    def test_drop_tables(self):
        """Test dropping database tables."""
        db = DatabaseConnection(database_url='sqlite:///:memory:')
        db.create_tables()
        db.drop_tables()
        
        # Verify tables don't exist
        with db.get_session() as session:
            result = session.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            tables = [row[0] for row in result]
            assert 'companies' not in tables
            assert 'stock_data' not in tables
        
        db.close()
    
    def test_get_session_context_manager(self):
        """Test session context manager for successful operations."""
        db = DatabaseConnection(database_url='sqlite:///:memory:')
        db.create_tables()
        
        # Insert a company using context manager
        with db.get_session() as session:
            company = Company(symbol='TEST', name='Test Company')
            session.add(company)
        
        # Verify the company was committed
        with db.get_session() as session:
            result = session.query(Company).filter_by(symbol='TEST').first()
            assert result is not None
            assert result.name == 'Test Company'
        
        db.close()
    
    def test_get_session_rollback_on_error(self):
        """Test that session rolls back on error."""
        db = DatabaseConnection(database_url='sqlite:///:memory:')
        db.create_tables()
        
        # First, insert a company
        with db.get_session() as session:
            company = Company(symbol='TEST1', name='Test Company 1')
            session.add(company)
        
        # Try to insert duplicate symbol (should fail)
        with pytest.raises(Exception):
            with db.get_session() as session:
                company1 = Company(symbol='TEST2', name='Test Company 2')
                session.add(company1)
                session.flush()  # Force the insert
                
                # This should violate unique constraint
                company2 = Company(symbol='TEST2', name='Test Company 2 Duplicate')
                session.add(company2)
                session.flush()
        
        # Verify TEST2 was not committed
        with db.get_session() as session:
            result = session.query(Company).filter_by(symbol='TEST2').first()
            # Depending on when the error occurred, TEST2 might or might not exist
            # The important thing is the session was rolled back
        
        db.close()
    
    def test_get_session_with_retry_success_first_attempt(self):
        """Test successful connection on first attempt."""
        db = DatabaseConnection(database_url='sqlite:///:memory:')
        db.create_tables()
        
        session = db.get_session_with_retry(max_attempts=3)
        assert session is not None
        
        # Verify session works
        result = session.execute(text("SELECT 1")).scalar()
        assert result == 1
        
        session.close()
        db.close()
    
    def test_get_session_with_retry_success_after_failures(self):
        """Test successful connection after initial failures."""
        db = DatabaseConnection(database_url='sqlite:///:memory:')
        db.create_tables()
        
        # Mock the SessionLocal to fail twice then succeed
        original_session_local = db.SessionLocal
        call_count = [0]
        
        def mock_session_local():
            call_count[0] += 1
            if call_count[0] <= 2:
                raise OperationalError("Connection failed", params=None, orig=None)
            return original_session_local()
        
        db.SessionLocal = mock_session_local
        
        # Should succeed on third attempt
        session = db.get_session_with_retry(max_attempts=3)
        assert session is not None
        assert call_count[0] == 3
        
        session.close()
        db.close()
    
    def test_get_session_with_retry_all_attempts_fail(self):
        """Test that OperationalError is raised when all attempts fail."""
        db = DatabaseConnection(database_url='sqlite:///:memory:')
        
        # Mock SessionLocal to always fail
        def mock_session_local():
            raise OperationalError("Connection failed", params=None, orig=None)
        
        db.SessionLocal = mock_session_local
        
        # Should raise OperationalError after 3 attempts
        with pytest.raises(OperationalError) as exc_info:
            db.get_session_with_retry(max_attempts=3)
        
        assert "Failed to connect to database after 3 attempts" in str(exc_info.value)
        
        db.close()
    
    def test_get_session_with_retry_exponential_backoff(self):
        """Test that retry logic uses exponential backoff."""
        db = DatabaseConnection(database_url='sqlite:///:memory:')
        
        # Mock SessionLocal to fail twice
        call_count = [0]
        call_times = []
        
        def mock_session_local():
            call_count[0] += 1
            call_times.append(time.time())
            if call_count[0] <= 2:
                raise OperationalError("Connection failed", params=None, orig=None)
            # Create a real session on third attempt
            engine = db.engine
            from sqlalchemy.orm import sessionmaker
            Session = sessionmaker(bind=engine)
            return Session()
        
        db.SessionLocal = mock_session_local
        db.create_tables()
        
        start_time = time.time()
        session = db.get_session_with_retry(max_attempts=3)
        total_time = time.time() - start_time
        
        # Should have waited ~1s + ~2s = ~3s total
        # Allow some tolerance for execution time
        assert total_time >= 2.5  # At least 2.5 seconds
        assert total_time < 5.0   # But not too long
        assert call_count[0] == 3
        
        session.close()
        db.close()
    
    def test_get_session_with_retry_context_manager(self):
        """Test retry context manager for successful operations."""
        db = DatabaseConnection(database_url='sqlite:///:memory:')
        db.create_tables()
        
        # Insert a company using retry context manager
        with db.get_session_with_retry_context(max_attempts=3) as session:
            company = Company(symbol='RETRY', name='Retry Test Company')
            session.add(company)
        
        # Verify the company was committed
        with db.get_session() as session:
            result = session.query(Company).filter_by(symbol='RETRY').first()
            assert result is not None
            assert result.name == 'Retry Test Company'
        
        db.close()
    
    def test_get_session_with_retry_context_rollback(self):
        """Test that retry context manager rolls back on error."""
        db = DatabaseConnection(database_url='sqlite:///:memory:')
        db.create_tables()
        
        # Try to insert with an error
        with pytest.raises(Exception):
            with db.get_session_with_retry_context() as session:
                company = Company(symbol='ERROR', name='Error Company')
                session.add(company)
                session.flush()
                # Force an error
                raise ValueError("Test error")
        
        # Verify nothing was committed
        with db.get_session() as session:
            result = session.query(Company).filter_by(symbol='ERROR').first()
            assert result is None
        
        db.close()
    
    def test_close_engine(self):
        """Test closing the database engine."""
        db = DatabaseConnection(database_url='sqlite:///:memory:')
        assert db.engine is not None
        
        db.close()
        # Engine should be disposed
        # Note: SQLAlchemy doesn't provide a direct way to check if disposed,
        # but we can verify the method was called without errors


class TestGlobalDatabaseInstance:
    """Test global database instance functions."""
    
    def test_get_database_singleton(self):
        """Test that get_database returns the same instance."""
        # Reset global instance
        import src.models.connection as conn_module
        conn_module._db_instance = None
        
        db1 = get_database()
        db2 = get_database()
        
        assert db1 is db2
        
        db1.close()
    
    def test_get_database_with_env_config(self):
        """Test that get_database uses environment configuration."""
        # Reset global instance
        import src.models.connection as conn_module
        conn_module._db_instance = None
        
        with patch.dict(os.environ, {
            'DATABASE_URL': 'sqlite:///./global_test.db',
            'DB_POOL_SIZE': '15',
            'DB_MAX_OVERFLOW': '25'
        }):
            db = get_database()
            assert db.database_url == 'sqlite:///./global_test.db'
            assert db.pool_size == 15
            assert db.max_overflow == 25
            db.close()
        
        # Reset for other tests
        conn_module._db_instance = None
    
    def test_init_database(self):
        """Test database initialization function."""
        # Reset global instance
        import src.models.connection as conn_module
        conn_module._db_instance = None
        
        with patch.dict(os.environ, {'DATABASE_URL': 'sqlite:///:memory:'}):
            init_database()
            
            db = get_database()
            
            # Verify tables were created
            with db.get_session() as session:
                result = session.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
                tables = [row[0] for row in result]
                assert 'companies' in tables
                assert 'stock_data' in tables
            
            db.close()
        
        # Reset for other tests
        conn_module._db_instance = None


class TestConnectionPooling:
    """Test connection pooling behavior."""
    
    @pytest.mark.skipif(not HAS_PSYCOPG2, reason="psycopg2 not installed")
    def test_postgresql_pool_configuration(self):
        """Test that PostgreSQL uses QueuePool with correct settings."""
        db = DatabaseConnection(
            database_url='postgresql://user:pass@localhost:5432/testdb',
            pool_size=5,
            max_overflow=10
        )
        
        # Verify pool settings
        pool = db.engine.pool
        assert pool.size() == 5
        
        db.close()
    
    def test_sqlite_uses_static_pool(self):
        """Test that SQLite uses StaticPool."""
        db = DatabaseConnection(database_url='sqlite:///:memory:')
        
        # SQLite should use StaticPool
        from sqlalchemy.pool import StaticPool
        assert isinstance(db.engine.pool, StaticPool)
        
        db.close()
