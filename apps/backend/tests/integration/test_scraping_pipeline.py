# apps/backend/tests/integration/test_scraping_pipeline.py
import pytest
import time
from pathlib import Path
import tempfile
from unittest.mock import patch, Mock

from src.agents.queue_manager import SQLiteQueueManager
from src.agents.scraping_worker import ScrapingWorker
from src.agents.citation_detector import CitationDetector
from src.utils.legal_reference_parser import LegalReference


class TestScrapingPipeline:
    """Integration tests for the complete scraping pipeline."""

    @pytest.fixture
    def temp_docs_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def queue_manager(self):
        manager = SQLiteQueueManager(":memory:")
        yield manager
        manager.close()

    def test_end_to_end_citation_to_document(
        self,
        queue_manager,
        temp_docs_dir
    ):
        """Test complete flow: detect citation -> enqueue -> scrape -> save."""

        # Step 1: Detect citations from response
        detector = CitationDetector()
        response = "Conforme estabelecido pela LC 227/2026, artigo 5º..."
        chunks = []

        citations = detector.detect(response, chunks)
        assert len(citations) > 0

        # Step 2: Enqueue jobs (simulating queue enrichment)
        for citation in citations:
            # In real implementation, URL would come from URLResolver
            queue_manager.enqueue(
                citation,
                f"https://example.com/{citation.normalized}",
                priority=1
            )

        # Step 3: Worker processes job
        with patch('src.services.firecrawl_service.requests') as mock_requests:
            # Mock successful Firecrawl response (must be > 100 chars)
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'data': {
                    'markdown': '# Lei Complementar 227/2026\n\nArtigo 1º... ' + 'Content ' * 20
                }
            }
            mock_requests.post.return_value = mock_response

            worker = ScrapingWorker(
                queue_manager=queue_manager,
                poll_interval=0.1,
                docs_path=str(temp_docs_dir)
            )

            # Process one job
            job = queue_manager.get_next_job()
            assert job is not None
            worker._process_job(job)

        # Step 4: Verify document was saved
        expected_file = temp_docs_dir / f"{citations[0].normalized}.md"
        assert expected_file.exists()

        content = expected_file.read_text()
        assert "Lei Complementar 227/2026" in content

        # Step 5: Verify job marked as completed
        next_job = queue_manager.get_next_job()
        assert next_job is None

    def test_worker_handles_multiple_jobs(self, queue_manager, temp_docs_dir):
        """Test worker processes multiple jobs in priority order."""

        refs = [
            LegalReference(normalized="LC-227-2026", type="LC"),
            LegalReference(normalized="LC-228-2026", type="LC"),
            LegalReference(normalized="DEC-11374-2023", type="DEC"),
        ]

        # Enqueue with different priorities
        queue_manager.enqueue(refs[0], "https://example.com/1", priority=1)
        queue_manager.enqueue(refs[1], "https://example.com/2", priority=5)
        queue_manager.enqueue(refs[2], "https://example.com/3", priority=3)

        with patch('src.services.firecrawl_service.requests') as mock_requests:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'data': {'markdown': '# Content\n\n' + 'Legal document content. ' * 10}
            }
            mock_requests.post.return_value = mock_response

            worker = ScrapingWorker(
                queue_manager=queue_manager,
                poll_interval=0.1,
                docs_path=str(temp_docs_dir)
            )

            # Process all jobs
            processed_order = []
            for _ in range(3):
                job = queue_manager.get_next_job()
                if job:
                    processed_order.append(job.legal_reference)
                    worker._process_job(job)

        # Verify processed in priority order (highest first)
        assert processed_order[0] == "LC-228-2026"  # priority 5
        assert processed_order[1] == "DEC-11374-2023"  # priority 3
        assert processed_order[2] == "LC-227-2026"  # priority 1
