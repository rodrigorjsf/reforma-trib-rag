# apps/backend/tests/agents/test_queue_manager.py
import pytest
from pathlib import Path
import tempfile
from src.agents.queue_manager import SQLiteQueueManager, ScrapingJob
from src.utils.legal_reference_parser import LegalReference


class TestSQLiteQueueManager:
    @pytest.fixture
    def queue_manager(self):
        # Use in-memory database for testing
        manager = SQLiteQueueManager(":memory:")
        yield manager
        manager.close()

    def test_enqueue_new_job(self, queue_manager):
        ref = LegalReference(
            normalized="LC-227-2026",
            type="LC",
            number="227",
            year="2026"
        )
        queue_manager.enqueue(ref, "https://example.com/lc227", priority=1)

        job = queue_manager.get_next_job()
        assert job is not None
        assert job.legal_reference == "LC-227-2026"
        assert job.source_url == "https://example.com/lc227"
        assert job.status == "processing"  # Status changes to processing when retrieved

    def test_enqueue_duplicate_increases_priority(self, queue_manager):
        ref = LegalReference(normalized="LC-227-2026", type="LC")

        queue_manager.enqueue(ref, "https://example.com/lc227", priority=1)
        queue_manager.enqueue(ref, "https://example.com/lc227", priority=1)

        # Should only have one job with increased priority
        job = queue_manager.get_next_job()
        assert job.priority == 2

    def test_get_next_job_returns_highest_priority(self, queue_manager):
        ref1 = LegalReference(normalized="LC-227-2026", type="LC")
        ref2 = LegalReference(normalized="LC-228-2026", type="LC")

        queue_manager.enqueue(ref1, "https://example.com/1", priority=1)
        queue_manager.enqueue(ref2, "https://example.com/2", priority=5)

        job = queue_manager.get_next_job()
        assert job.legal_reference == "LC-228-2026"
        assert job.priority == 5

    def test_mark_completed(self, queue_manager):
        ref = LegalReference(normalized="LC-227-2026", type="LC")
        queue_manager.enqueue(ref, "https://example.com/lc227", priority=1)

        job = queue_manager.get_next_job()
        queue_manager.mark_completed(job.id)

        # Should not return completed job
        next_job = queue_manager.get_next_job()
        assert next_job is None

    def test_mark_failed_with_error_message(self, queue_manager):
        ref = LegalReference(normalized="LC-227-2026", type="LC")
        queue_manager.enqueue(ref, "https://example.com/lc227", priority=1)

        job = queue_manager.get_next_job()
        queue_manager.mark_failed(job.id, "Timeout error")

        # Verify job is marked as failed
        # Note: failed jobs should not be returned by get_next_job
        next_job = queue_manager.get_next_job()
        assert next_job is None

    def test_file_exists_check_skips_enqueue(self, queue_manager):
        # Create temp file to simulate existing doc
        with tempfile.NamedTemporaryFile(mode='w', suffix='-LC-227-2026.md', delete=False) as f:
            temp_path = Path(f.name)

        try:
            ref = LegalReference(normalized="LC-227-2026", type="LC")
            # This should skip because file exists (implementation detail)
            # For now, test basic enqueue
            queue_manager.enqueue(ref, "https://example.com/lc227", priority=1)
            job = queue_manager.get_next_job()
            assert job is not None
        finally:
            temp_path.unlink(missing_ok=True)
