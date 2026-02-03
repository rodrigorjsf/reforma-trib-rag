import pytest
from unittest.mock import Mock, patch
from src.ingestion.scrapers.planalto_scraper import PlanaltoScraper
from src.ingestion.exceptions import ScrapingError


@pytest.fixture
def sample_html():
    """Sample Planalto HTML structure"""
    return """
    <html>
    <head><title>Lei Complementar 214/2024</title></head>
    <body>
        <h1>LEI COMPLEMENTAR Nº 214, DE 16 DE JANEIRO DE 2025</h1>
        <div class="texto">
            <p>Art. 1º Esta Lei Complementar institui a Contribuição sobre Bens e Serviços (CBS).</p>
            <p>§ 1º A CBS é um imposto sobre o valor agregado.</p>
            <p>Art. 2º O fato gerador da CBS é a operação com bens ou a prestação de serviços.</p>
        </div>
    </body>
    </html>
    """


def test_scraper_extracts_title(sample_html):
    """Test scraper extracts document title"""
    with patch('requests.get') as mock_get:
        mock_get.return_value.text = sample_html
        mock_get.return_value.status_code = 200

        scraper = PlanaltoScraper()
        result = scraper.scrape("https://example.com/lcp214.htm")

        assert "214" in result["source_id"]
        assert "COMPLEMENTAR" in result["title"]


def test_scraper_converts_to_markdown(sample_html):
    """Test scraper converts HTML to Markdown"""
    with patch('requests.get') as mock_get:
        mock_get.return_value.text = sample_html
        mock_get.return_value.status_code = 200

        scraper = PlanaltoScraper()
        result = scraper.scrape("https://example.com/lcp214.htm")

        assert "Art. 1º" in result["content"]
        assert "§ 1º" in result["content"]
        assert result["url"] == "https://example.com/lcp214.htm"


def test_scraper_handles_network_error():
    """Test scraper raises ScrapingError on network failure"""
    with patch('requests.get', side_effect=Exception("Network error")):
        scraper = PlanaltoScraper()

        with pytest.raises(ScrapingError, match="Network error"):
            scraper.scrape("https://example.com/test.htm")
