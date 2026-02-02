# apps/backend/src/agents/scraping_worker.py
import time
import logging
import shutil
from pathlib import Path
from typing import Optional
import os

from .queue_manager import QueueManager, ScrapingJob
from ..services.firecrawl_service import FirecrawlService

logger = logging.getLogger(__name__)


class ScrapingWorker:
    """Background worker that processes scraping queue."""

    def __init__(
        self,
        queue_manager: QueueManager,
        poll_interval: int = 5,
        docs_path: str = "./docs"
    ):
        """
        Initialize scraping worker.

        Args:
            queue_manager: Queue manager instance
            poll_interval: Seconds to wait between queue polls
            docs_path: Directory to save scraped documents
        """
        self.queue = queue_manager
        self.poll_interval = poll_interval
        self.docs_path = Path(docs_path)
        self.docs_path.mkdir(parents=True, exist_ok=True)

        # Initialize Firecrawl service
        timeout = int(os.getenv("FIRECRAWL_TIMEOUT", "60"))
        firecrawl_retries = int(os.getenv("FIRECRAWL_MAX_RETRIES", "3"))
        self.firecrawl = FirecrawlService(timeout=timeout, max_retries=firecrawl_retries)

        # Worker-level retry configuration
        self.max_retries = int(os.getenv("SCRAPING_WORKER_MAX_RETRIES", "3"))
        self.min_disk_space_gb = int(os.getenv("MIN_DISK_SPACE_GB", "1"))

        self._running = False

    def start(self):
        """Start the worker loop (blocking)."""
        self._running = True
        logger.info("Scraping worker started")

        while self._running:
            try:
                job = self.queue.get_next_job()

                if job:
                    self._process_job(job)
                else:
                    # No jobs available, sleep
                    time.sleep(self.poll_interval)

            except Exception as e:
                logger.error(f"Worker error: {e}")
                time.sleep(self.poll_interval)

    def stop(self):
        """Stop the worker loop."""
        self._running = False
        logger.info("Scraping worker stopped")

    def _process_job(self, job: ScrapingJob):
        """
        Process a single scraping job with retry logic.

        Args:
            job: ScrapingJob to process
        """
        logger.info(f"Processing job {job.id}: {job.legal_reference} (attempt {job.attempts + 1}/{self.max_retries})")

        try:
            # Check if file already exists (race condition check)
            doc_path = self.docs_path / f"{job.legal_reference}.md"
            if doc_path.exists():
                logger.info(f"Document already exists: {doc_path}")
                self.queue.mark_completed(job.id)
                return

            # Scrape document
            content = self._scrape_document(job.source_url)

            if content is None:
                # Handle retry logic
                if job.attempts + 1 < self.max_retries:
                    self.queue.mark_pending(job.id)
                    backoff = 30 * (2 ** job.attempts)
                    logger.warning(f"Scraping failed for job {job.id}, will retry after {backoff}s")
                    time.sleep(backoff)
                else:
                    self.queue.mark_failed(job.id, "Max retries exceeded after scraping failures")
                return

            # Validate content
            if len(content) < 100:
                error_msg = f"Content too short: {len(content)} characters"
                logger.warning(error_msg)
                if job.attempts + 1 < self.max_retries:
                    self.queue.mark_pending(job.id)
                else:
                    self.queue.mark_failed(job.id, error_msg)
                return

            # Save document
            self._save_document(content, job.legal_reference)

            # TODO: Index in ChromaDB
            # self._index_document(content, job.legal_reference)

            # Mark as completed
            self.queue.mark_completed(job.id)
            logger.info(f"Successfully completed job {job.id}")

        except IOError as e:
            # Disk space or permission errors - don't retry
            error_msg = f"IO error: {str(e)}"
            logger.error(error_msg)
            self.queue.mark_failed(job.id, error_msg)
        except Exception as e:
            # Other unexpected errors - retry if possible
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            if job.attempts + 1 < self.max_retries:
                self.queue.mark_pending(job.id)
            else:
                self.queue.mark_failed(job.id, error_msg)

    def _scrape_document(self, url: str) -> Optional[str]:
        """
        Scrape document from URL.

        Args:
            url: URL to scrape

        Returns:
            Markdown content or None if failed
        """
        return self.firecrawl.scrape(url)

    def _save_document(self, content: str, reference: str):
        """
        Save scraped document to disk with disk space check.

        Args:
            content: Document content
            reference: Normalized legal reference (used as filename)

        Raises:
            IOError: If insufficient disk space
        """
        # Check available disk space
        stat = shutil.disk_usage(self.docs_path)
        available_gb = stat.free / (1024**3)

        if available_gb < self.min_disk_space_gb:
            raise IOError(
                f"Insufficient disk space: {available_gb:.2f}GB available, "
                f"{self.min_disk_space_gb}GB required"
            )

        doc_path = self.docs_path / f"{reference}.md"

        with open(doc_path, 'w', encoding='utf-8') as f:
            f.write(content)

        logger.info(f"Saved document to {doc_path} ({len(content)} bytes, {available_gb:.2f}GB free)")

    def _index_document(self, content: str, reference: str):
        """
        Index document in ChromaDB.

        Args:
            content: Document content
            reference: Legal reference

        TODO: Implement ChromaDB indexing
        """
        pass
