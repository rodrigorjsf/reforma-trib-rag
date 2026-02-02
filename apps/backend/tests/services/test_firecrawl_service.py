# apps/backend/tests/services/test_firecrawl_service.py
import pytest
from unittest.mock import Mock, patch
from src.services.firecrawl_service import FirecrawlService


class TestFirecrawlService:
    @pytest.fixture
    def service(self):
        return FirecrawlService(timeout=30, max_retries=2)

    @patch('src.services.firecrawl_service.requests')
    def test_scrape_success(self, mock_requests, service):
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': {
                'markdown': '# Lei Complementar 227\n\nContent here...'
            }
        }
        mock_requests.post.return_value = mock_response

        content = service.scrape("https://example.com/lei")
        assert content is not None
        assert "Lei Complementar 227" in content

    @patch('src.services.firecrawl_service.requests')
    def test_scrape_timeout_retries(self, mock_requests, service):
        # Mock timeout on first call, success on second
        mock_requests.post.side_effect = [
            Exception("Timeout"),
            Mock(status_code=200, json=lambda: {'data': {'markdown': 'Content'}})
        ]

        content = service.scrape("https://example.com/lei")
        assert content is not None
        assert mock_requests.post.call_count == 2

    @patch('src.services.firecrawl_service.requests')
    def test_scrape_404_returns_none(self, mock_requests, service):
        mock_response = Mock()
        mock_response.status_code = 404
        mock_requests.post.return_value = mock_response

        content = service.scrape("https://example.com/nonexistent")
        assert content is None

    @patch('src.services.firecrawl_service.requests')
    def test_scrape_max_retries_exceeded(self, mock_requests, service):
        # All retries fail
        mock_requests.post.side_effect = Exception("Persistent error")

        content = service.scrape("https://example.com/lei")
        assert content is None
        assert mock_requests.post.call_count == service.max_retries
