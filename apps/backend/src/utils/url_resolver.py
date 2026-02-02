# apps/backend/src/utils/url_resolver.py
import json
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class URLResolver:
    """Resolves legal references to their source URLs from SUB-LINKS file."""

    def __init__(self, links_file_path: str):
        """
        Initialize resolver with links file.

        Args:
            links_file_path: Path to LCP214-25-SUB-LINKS.md JSON file
        """
        self.links_file_path = Path(links_file_path)
        self.links_map: dict[str, str] = {}
        self._load_links()

    def _load_links(self):
        """Load and parse the links file into a searchable map."""
        try:
            with open(self.links_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # The file contains JSON with hyperlinks array
                data = json.loads(content)
                hyperlinks = data.get('hyperlinks', [])

                for link in hyperlinks:
                    url = link.get('url', '')
                    legal_ref = link.get('legal_reference', '')

                    # Store URL by reference text for fuzzy matching
                    if url and legal_ref:
                        # Store original reference
                        self.links_map[legal_ref] = url

                        # Also try to extract and normalize common patterns
                        # This will be matched against normalized refs
                        if 'Lei Complementar' in legal_ref or 'LC' in legal_ref:
                            # Try to extract number and year
                            import re
                            match = re.search(r'(\d+).*?(\d{4})', legal_ref)
                            if match:
                                normalized_key = f"LC-{match.group(1)}-{match.group(2)}"
                                self.links_map[normalized_key] = url

                        elif 'Constituição Federal' in legal_ref or 'CF' in legal_ref:
                            # For CF articles
                            if 'Constituicao' in url:
                                self.links_map['CF-art-156A'] = url

                logger.info(f"Loaded {len(self.links_map)} links from {self.links_file_path}")

        except FileNotFoundError:
            logger.error(f"Links file not found: {self.links_file_path}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse links file as JSON: {e}")
        except Exception as e:
            logger.error(f"Unexpected error loading links: {e}")

    def resolve(self, normalized_reference: str) -> Optional[str]:
        """
        Resolve a normalized legal reference to its source URL.

        Args:
            normalized_reference: Normalized reference like "LC-227-2026"

        Returns:
            URL string or None if not found
        """
        # Direct lookup
        if normalized_reference in self.links_map:
            return self.links_map[normalized_reference]

        # Fuzzy search by checking if any key contains the reference parts
        # For example, "LC-227-2026" should match entries containing "227" and "2026"
        if '-' in normalized_reference:
            parts = normalized_reference.split('-')
            for key, url in self.links_map.items():
                if all(part.lower() in key.lower() for part in parts if part):
                    return url

        return None
