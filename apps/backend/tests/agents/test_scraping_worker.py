# apps/backend/tests/agents/test_scraping_worker.py
import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import tempfile
from src.agents.scraping_worker import ScrapingWorker
from src.agents.queue_manager import SQLiteQueueManager, ScrapingJob
from src.utils.legal_reference_parser import LegalReference


class TestScrapingWorker:
    @pytest.fixture
    def queue_manager(self):
        manager = SQLiteQueueManager(":memory:")
        yield manager
        manager.close()

    @pytest.fixture
    def worker(self, queue_manager):
        with patch('src.agents.scraping_worker.FirecrawlService'):
            worker = ScrapingWorker(queue_manager, poll_interval=0.1, docs_path="./test_docs")
            yield worker

    def test_process_job_success(self, worker, queue_manager):
        # Mock firecrawl to return content (must be > 100 chars for validation)
        worker.firecrawl.scrape = Mock(return_value="# Lei Complementar 227/2026\n\n" + "Article 1... " * 10)

        # Mock file operations
        with patch('pathlib.Path.mkdir'), \
             patch('builtins.open', create=True) as mock_open:

            # Enqueue job
            ref = LegalReference(normalized="LC-227-2026", type="LC")
            queue_manager.enqueue(ref, "https://example.com/lc227", priority=1)

            # Process job
            job = queue_manager.get_next_job()
            worker._process_job(job)

            # Verify file was written
            mock_open.assert_called_once()
            # Verify job marked as completed
            next_job = queue_manager.get_next_job()
            assert next_job is None

    def test_process_job_scraping_failure(self, worker, queue_manager):
        # Mock firecrawl to fail
        worker.firecrawl.scrape = Mock(return_value=None)
        # Disable retry sleep for faster tests
        worker.max_retries = 1

        ref = LegalReference(normalized="LC-227-2026", type="LC")
        queue_manager.enqueue(ref, "https://example.com/lc227", priority=1)

        job = queue_manager.get_next_job()
        worker._process_job(job)

        # Job should be marked as failed after max retries
        # Verify by trying to get next job (should be None since failed jobs are skipped)
        next_job = queue_manager.get_next_job()
        assert next_job is None

    def test_save_document_creates_file(self, worker):
        with tempfile.TemporaryDirectory() as tmpdir:
            worker.docs_path = Path(tmpdir)
            content = "# Test Content"
            ref = "LC-227-2026"

            worker._save_document(content, ref)

            saved_file = worker.docs_path / f"{ref}.md"
            assert saved_file.exists()
            assert saved_file.read_text() == content
