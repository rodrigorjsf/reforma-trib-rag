"""Scraper for Planalto legal documents."""

import hashlib
import re
from datetime import datetime, timezone
from typing import Dict

import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md

from ..exceptions import ScrapingError


class PlanaltoScraper:
    """Scraper for planalto.gov.br legal documents."""

    def __init__(self, timeout: int = 30):
        """Initialize scraper.

        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout

    def scrape(self, url: str) -> Dict:
        """Scrape legal document from Planalto.

        Args:
            url: URL of the document to scrape

        Returns:
            Dictionary with:
                - source_id: Extracted law identifier (e.g., "LC_214_2024")
                - title: Document title
                - content: Document content in Markdown
                - url: Original URL
                - scraped_at: Timestamp
                - content_hash: SHA256 hash of content

        Raises:
            ScrapingError: If scraping fails
        """
        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            html = response.text
        except Exception as e:
            raise ScrapingError(f"Failed to fetch {url}: {e}")

        try:
            soup = BeautifulSoup(html, 'html.parser')

            # Extract title
            title_tag = soup.find('h1')
            title = title_tag.text.strip() if title_tag else "Untitled"

            # Extract source_id from title
            source_id = self._extract_source_id(title)

            # Extract main content
            content_div = soup.find('div', class_='texto') or soup.find('article')
            if not content_div:
                raise ScrapingError(f"Could not find content in {url}")

            # Convert HTML to Markdown
            markdown_content = md(str(content_div), heading_style="ATX")

            # Compute content hash
            content_hash = hashlib.sha256(
                markdown_content.encode('utf-8')
            ).hexdigest()

            return {
                "source_id": source_id,
                "title": title,
                "content": markdown_content,
                "url": url,
                "scraped_at": datetime.now(timezone.utc).isoformat(),
                "content_hash": content_hash
            }

        except ScrapingError:
            raise
        except Exception as e:
            raise ScrapingError(f"Failed to parse {url}: {e}")

    def _extract_source_id(self, title: str) -> str:
        """Extract source ID from document title.

        Examples:
            "LEI COMPLEMENTAR Nº 214, DE 16 DE JANEIRO DE 2025" -> "LC_214_2025"
            "DECRETO Nº 12.345 DE 2024" -> "DECRETO_12345_2024"
        """
        # Try to match Lei Complementar
        lc_match = re.search(r'LEI\s+COMPLEMENTAR\s+N[ºÃ]\s*(\d+)[^0-9]*(\d{4})', title, re.IGNORECASE)
        if lc_match:
            return f"LC_{lc_match.group(1)}_{lc_match.group(2)}"

        # Try to match Decreto
        decreto_match = re.search(r'DECRETO\s+N[ºÃ]\s*([\d.]+)[^0-9]*(\d{4})', title, re.IGNORECASE)
        if decreto_match:
            number = decreto_match.group(1).replace('.', '')
            return f"DECRETO_{number}_{decreto_match.group(2)}"

        # Fallback: use hash of title
        title_hash = hashlib.sha256(title.encode()).hexdigest()[:8]
        return f"DOC_{title_hash}"
