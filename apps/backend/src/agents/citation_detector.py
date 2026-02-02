# apps/backend/src/agents/citation_detector.py
import re
from typing import List
import logging

from ..utils.legal_reference_parser import LegalReferenceParser, LegalReference

logger = logging.getLogger(__name__)


class CitationDetector:
    """Detects and normalizes legal citations from responses and chunk metadata."""

    def __init__(self):
        self.parser = LegalReferenceParser()

    def detect(self, response: str, retrieved_chunks: List[dict]) -> List[LegalReference]:
        """
        Detect all legal references from response text and chunk metadata.

        Args:
            response: LLM-generated response text
            retrieved_chunks: List of RAG chunks with metadata

        Returns:
            Deduplicated list of normalized LegalReference objects
        """
        # Extract from text
        text_refs = self._extract_from_text(response)

        # Extract from chunk metadata
        chunk_refs = self._extract_from_chunks(retrieved_chunks)

        # Merge and deduplicate
        all_raw_refs = text_refs + chunk_refs
        normalized_refs = self._normalize(all_raw_refs)

        # Deduplicate by normalized form
        seen = set()
        unique_refs = []
        for ref in normalized_refs:
            if ref.normalized not in seen:
                seen.add(ref.normalized)
                unique_refs.append(ref)

        logger.info(f"Detected {len(unique_refs)} unique legal references")
        return unique_refs

    def _extract_from_text(self, text: str) -> List[str]:
        """
        Extract legal reference strings from text using regex patterns.

        Args:
            text: Text to scan for references

        Returns:
            List of raw reference strings
        """
        references = []

        # Use the same patterns as LegalReferenceParser
        patterns = self.parser.PATTERNS

        for pattern_name, pattern in patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                # Store the full matched text
                references.append(match.group(0))

        return references

    def _extract_from_chunks(self, chunks: List[dict]) -> List[str]:
        """
        Extract legal references from chunk metadata.

        Args:
            chunks: List of chunk dictionaries with metadata

        Returns:
            List of raw reference strings
        """
        references = []

        for chunk in chunks:
            metadata = chunk.get('metadata', {})
            legal_refs = metadata.get('legal_references', [])

            if isinstance(legal_refs, list):
                references.extend(legal_refs)
            elif isinstance(legal_refs, str):
                references.append(legal_refs)

        return references

    def _normalize(self, raw_refs: List[str]) -> List[LegalReference]:
        """
        Normalize raw reference strings to LegalReference objects.

        Args:
            raw_refs: List of raw reference strings

        Returns:
            List of normalized LegalReference objects
        """
        normalized = []

        for ref in raw_refs:
            parsed = self.parser.normalize(ref)
            if parsed is not None:
                normalized.append(parsed)
            else:
                logger.warning(f"Failed to normalize reference: {ref}")

        return normalized
