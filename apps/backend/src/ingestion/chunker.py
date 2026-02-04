"""Hybrid chunker for legal documents.

Splits by articles (Art. X) and paragraphs (§) while respecting token limits.
"""

import re
from typing import List

from .metadata_extractor import MetadataExtractor
from .models import ChunkType, LegalChunk
from .token_counter import TokenCounter


class HybridChunker:
    """Hybrid chunker that respects legal structure and token limits.

    Strategy:
        1. Split by articles (Art. X)
        2. If article > max_chunk_size, split by paragraphs (§)
        3. Extract metadata for each chunk
        4. Count tokens
    """

    def __init__(
        self,
        max_chunk_size: int = 800,
        min_chunk_size: int = 100,
        encoding_name: str = "cl100k_base",
    ):
        """Initialize chunker.

        Args:
            max_chunk_size: Maximum tokens per chunk
            min_chunk_size: Minimum tokens per chunk
            encoding_name: Tiktoken encoding name
        """
        self.max_chunk_size = max_chunk_size
        self.min_chunk_size = min_chunk_size
        self.token_counter = TokenCounter(encoding_name)
        self.metadata_extractor = MetadataExtractor()

    def chunk_document(
        self,
        content: str,
        source_id: str,
        url: str,
    ) -> List[LegalChunk]:
        """Chunk a legal document.

        Args:
            content: Markdown content of document
            source_id: Document identifier (e.g., "LC_214_2024")
            url: Source URL

        Returns:
            List of LegalChunk objects
        """
        chunks = []

        # Split by articles first
        article_blocks = self._split_by_articles(content)

        for block in article_blocks:
            # Extract metadata
            metadata = self.metadata_extractor.extract_all(block)
            artigo = metadata.get("artigo")

            # Count tokens
            token_count = self.token_counter.count(block)

            # Check if block contains paragraphs
            has_paragraphs = bool(metadata.get("paragrafos"))

            # If block has paragraphs or is too large, split by paragraphs
            if has_paragraphs or token_count > self.max_chunk_size:
                paragraph_chunks = self._split_by_paragraphs(
                    block, artigo, source_id, url
                )
                chunks.extend(paragraph_chunks)
            else:
                # Create single chunk for article
                chunk = LegalChunk(
                    text=block.strip(),
                    source_id=source_id,
                    artigo=artigo or "Unknown",
                    paragrafo=None,
                    inciso=None,
                    chunk_type=ChunkType.ARTICLE,
                    token_count=token_count,
                    metadata={"url": url},
                )
                chunks.append(chunk)

        return chunks

    def _split_by_articles(self, content: str) -> List[str]:
        """Split content by articles.

        Args:
            content: Markdown content

        Returns:
            List of article blocks
        """
        # Pattern matches "Art. 123" or "Art. 123-A"
        pattern = r"(Art\.\s*\d+(?:-[A-Z])?)"

        # Split by article pattern
        parts = re.split(pattern, content)

        # Reconstruct article blocks
        blocks = []
        for i in range(1, len(parts), 2):
            if i < len(parts) - 1:
                article_header = parts[i]
                article_body = parts[i + 1]
                blocks.append(article_header + article_body)

        return blocks

    def _split_by_paragraphs(
        self, article_text: str, artigo: str, source_id: str, url: str
    ) -> List[LegalChunk]:
        """Split large article by paragraphs.

        Args:
            article_text: Text of article
            artigo: Article number (e.g., "Art. 1")
            source_id: Document identifier
            url: Source URL

        Returns:
            List of paragraph chunks
        """
        chunks = []

        # Pattern matches "§ 1º" or "§ 12º"
        pattern = r"(§\s*\d+º)"

        # Split by paragraph pattern
        parts = re.split(pattern, article_text)

        # First part is article header (before first §)
        if parts[0].strip():
            metadata = self.metadata_extractor.extract_all(parts[0])
            token_count = self.token_counter.count(parts[0])

            chunk = LegalChunk(
                text=parts[0].strip(),
                source_id=source_id,
                artigo=artigo or metadata.get("artigo") or "Unknown",
                paragrafo=None,
                inciso=None,
                chunk_type=ChunkType.ARTICLE,
                token_count=token_count,
                metadata={"url": url},
            )
            chunks.append(chunk)

        # Process paragraphs
        for i in range(1, len(parts), 2):
            if i < len(parts) - 1:
                paragraph_header = parts[i]
                paragraph_body = parts[i + 1]
                paragraph_text = paragraph_header + paragraph_body

                metadata = self.metadata_extractor.extract_all(paragraph_text)
                token_count = self.token_counter.count(paragraph_text)

                chunk = LegalChunk(
                    text=paragraph_text.strip(),
                    source_id=source_id,
                    artigo=artigo or metadata.get("artigo") or "Unknown",
                    paragrafo=metadata.get("paragrafos")[0]
                    if metadata.get("paragrafos")
                    else None,
                    inciso=None,
                    chunk_type=ChunkType.PARAGRAPH,
                    token_count=token_count,
                    metadata={"url": url},
                )
                chunks.append(chunk)

        return chunks
