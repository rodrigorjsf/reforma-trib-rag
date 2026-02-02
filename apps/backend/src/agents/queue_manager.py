# apps/backend/src/agents/queue_manager.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import logging

from ..db.connection import DatabaseConnection
from ..utils.legal_reference_parser import LegalReference

logger = logging.getLogger(__name__)


@dataclass
class ScrapingJob:
    """Represents a scraping job from the queue."""
    id: int
    legal_reference: str
    source_url: str
    status: str
    attempts: int
    priority: int
    error_message: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class QueueManager(ABC):
    """Abstract interface for managing scraping queue."""

    @abstractmethod
    def enqueue(self, ref: LegalReference, url: str, priority: int):
        """Add a new scraping job to the queue."""
        pass

    @abstractmethod
    def get_next_job(self) -> Optional[ScrapingJob]:
        """Get the next pending job with highest priority."""
        pass

    @abstractmethod
    def mark_completed(self, job_id: int):
        """Mark a job as successfully completed."""
        pass

    @abstractmethod
    def mark_failed(self, job_id: int, error: str):
        """Mark a job as failed with error message."""
        pass

    @abstractmethod
    def mark_pending(self, job_id: int):
        """Reset job to pending status for retry."""
        pass

    @abstractmethod
    def close(self):
        """Close database connection."""
        pass


class SQLiteQueueManager(QueueManager):
    """SQLite implementation of queue manager."""

    def __init__(self, db_path: str):
        """
        Initialize queue manager with SQLite database.

        Args:
            db_path: Path to SQLite database or ":memory:" for in-memory
        """
        self.db = DatabaseConnection(db_path)
        self.db.initialize_schema()

    def enqueue(self, ref: LegalReference, url: str, priority: int = 1):
        """Add a new scraping job to the queue or increment priority if exists."""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        try:
            # Try to insert new job
            cursor.execute(
                """
                INSERT INTO scraping_queue (legal_reference, source_url, priority)
                VALUES (?, ?, ?)
                """,
                (ref.normalized, url, priority)
            )
            conn.commit()
            logger.info(f"Enqueued new job: {ref.normalized}")

        except Exception as e:
            # If duplicate, increment priority
            if "UNIQUE constraint failed" in str(e):
                cursor.execute(
                    """
                    UPDATE scraping_queue
                    SET priority = priority + ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE legal_reference = ? AND status != 'failed'
                    """,
                    (priority, ref.normalized)
                )
                conn.commit()
                logger.info(f"Incremented priority for existing job: {ref.normalized}")
            else:
                logger.error(f"Failed to enqueue job: {e}")
                raise

    def get_next_job(self) -> Optional[ScrapingJob]:
        """Get the next pending job with highest priority."""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, legal_reference, source_url, status, attempts, priority,
                   error_message, created_at, updated_at
            FROM scraping_queue
            WHERE status = 'pending'
            ORDER BY priority DESC, created_at ASC
            LIMIT 1
            """
        )

        row = cursor.fetchone()
        if row is None:
            return None

        # Mark as processing
        cursor.execute(
            """
            UPDATE scraping_queue
            SET status = 'processing',
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (row['id'],)
        )
        conn.commit()

        return ScrapingJob(
            id=row['id'],
            legal_reference=row['legal_reference'],
            source_url=row['source_url'],
            status='processing',
            attempts=row['attempts'],
            priority=row['priority'],
            error_message=row['error_message'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )

    def mark_completed(self, job_id: int):
        """Mark a job as successfully completed."""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE scraping_queue
            SET status = 'completed',
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (job_id,)
        )
        conn.commit()
        logger.info(f"Marked job {job_id} as completed")

    def mark_failed(self, job_id: int, error: str):
        """Mark a job as failed with error message."""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE scraping_queue
            SET status = 'failed',
                attempts = attempts + 1,
                error_message = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (error, job_id)
        )
        conn.commit()
        logger.error(f"Marked job {job_id} as failed: {error}")

    def mark_pending(self, job_id: int):
        """Reset job to pending status for retry."""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE scraping_queue
            SET status = 'pending',
                attempts = attempts + 1,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (job_id,)
        )
        conn.commit()
        logger.info(f"Reset job {job_id} to pending for retry")

    def close(self):
        """Close database connection."""
        self.db.close()
