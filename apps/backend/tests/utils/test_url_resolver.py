# apps/backend/tests/utils/test_url_resolver.py
import pytest
from pathlib import Path
from src.utils.url_resolver import URLResolver


class TestURLResolver:
    @pytest.fixture
    def resolver(self):
        # Use the real SUB-LINKS file for integration testing
        links_file = Path(__file__).parent.parent.parent.parent.parent / "docs" / "LCP214-25-SUB-LINKS.md"
        return URLResolver(str(links_file))

    def test_resolve_existing_reference(self, resolver):
        # Test with a known reference from the links file
        url = resolver.resolve("LC-227-2026")
        assert url is not None
        assert "planalto.gov.br" in url

    def test_resolve_cf_reference(self, resolver):
        url = resolver.resolve("CF-art-156A")
        assert url is not None
        assert "Constituicao" in url or "constituicao" in url.lower()

    def test_resolve_nonexistent_reference_returns_none(self, resolver):
        url = resolver.resolve("LC-999-9999")
        assert url is None

    def test_load_links_file(self, resolver):
        # Verify links were loaded
        assert len(resolver.links_map) > 0
