"""Metadata extraction from legal documents using regex."""

import re
from typing import Dict, List, Optional


class MetadataExtractor:
    """Extracts legal metadata (Art, §, Inciso) from text using regex."""

    # Regex patterns
    ARTICLE_PATTERN = r'Art\.\s*(\d+(?:-[A-Z])?)'
    PARAGRAPH_PATTERN = r'§\s*(\d+)º'
    INCISO_PATTERN = r'\b([IVXLCDM]+)\s*[-–]'

    def extract_article(self, text: str) -> Optional[str]:
        """Extract article number from text.

        Examples:
            "Art. 46. texto" -> "Art. 46"
            "Art. 156-A. texto" -> "Art. 156-A"
        """
        match = re.search(self.ARTICLE_PATTERN, text)
        if match:
            return f"Art. {match.group(1)}"
        return None

    def extract_paragraph(self, text: str) -> Optional[str]:
        """Extract paragraph from text.

        Examples:
            "§ 1º texto" -> "§1º"
            "§ 12º texto" -> "§12º"
        """
        match = re.search(self.PARAGRAPH_PATTERN, text)
        if match:
            return f"§{match.group(1)}º"
        return None

    def extract_inciso(self, text: str) -> Optional[str]:
        """Extract inciso (Roman numeral) from text.

        Examples:
            "I - texto" -> "I"
            "XII - texto" -> "XII"
        """
        match = re.search(self.INCISO_PATTERN, text)
        if match:
            return match.group(1)
        return None

    def extract_all(self, text: str) -> Dict:
        """Extract all metadata from text.

        Returns:
            Dictionary with:
                - artigo: First article found
                - paragrafos: List of all paragraphs
                - incisos: List of all incisos
        """
        # Find all matches
        article = self.extract_article(text)

        # Find all paragraphs
        paragraphs = []
        for match in re.finditer(self.PARAGRAPH_PATTERN, text):
            paragraphs.append(f"§{match.group(1)}º")

        # Find all incisos
        incisos = []
        for match in re.finditer(self.INCISO_PATTERN, text):
            incisos.append(match.group(1))

        return {
            "artigo": article,
            "paragrafos": paragraphs,
            "incisos": incisos
        }
