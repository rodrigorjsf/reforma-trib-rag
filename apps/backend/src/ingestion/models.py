"""Data models for ingestion pipeline."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class ChunkType(str, Enum):
    """Type of legal chunk."""
    ARTICLE = "article"
    PARAGRAPH = "paragraph"
    AGGREGATED = "aggregated"


@dataclass
class LegalChunk:
    """Represents a chunk of legal text with metadata."""

    text: str
    source_id: str
    artigo: str
    paragrafo: Optional[str]
    inciso: Optional[str]
    chunk_type: ChunkType
    token_count: int
    metadata: dict = field(default_factory=dict)

    def get_citation(self) -> str:
        """Generate citation string for this chunk."""
        parts = [self.artigo]
        if self.paragrafo:
            parts.append(self.paragrafo)
        if self.inciso:
            parts.append(f"Inciso {self.inciso}")
        return f"[{', '.join(parts)} — {self.source_id}]"


@dataclass
class DocumentMetadata:
    """Metadata for scraped legal document."""

    source_id: str
    title: str
    url: str
    scraped_at: datetime
    content_hash: str
    document_type: str = "law"  # "law", "decree", "regulation"
