# apps/backend/src/db/connection.py
import sqlite3
import threading
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """Manages SQLite database connection and initialization."""

    def __init__(self, db_path: str):
        """
        Initialize database connection.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._connection: Optional[sqlite3.Connection] = None
        self._lock = threading.RLock()  # Reentrant lock for thread safety

    def get_connection(self) -> sqlite3.Connection:
        """Get or create database connection."""
        if self._connection is None:
            self._connection = sqlite3.connect(
                self.db_path,
                check_same_thread=False  # Allow usage across threads
            )
            self._connection.row_factory = sqlite3.Row  # Enable dict-like access
        return self._connection

    def initialize_schema(self):
        """Run migrations to initialize database schema."""
        migrations_dir = Path(__file__).parent / "migrations"
        migration_file = migrations_dir / "001_create_scraping_queue.sql"

        try:
            with open(migration_file, 'r') as f:
                migration_sql = f.read()

            conn = self.get_connection()
            conn.executescript(migration_sql)
            conn.commit()
            logger.info(f"Database schema initialized at {self.db_path}")

        except FileNotFoundError:
            logger.error(f"Migration file not found: {migration_file}")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize schema: {e}")
            raise

    def execute_write(self, query: str, params: tuple):
        """
        Execute write operation with thread-safe lock.

        Args:
            query: SQL query string with ? placeholders
            params: Tuple of parameters for the query

        Returns:
            Cursor object after execution
        """
        with self._lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor

    def close(self):
        """Close database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None
