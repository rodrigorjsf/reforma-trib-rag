"""Ingestion module for legal document processing."""

from .models import LegalChunk, ChunkType, DocumentMetadata
from .exceptions import IngestionError, ScrapingError, ChunkingError

__all__ = [
    "LegalChunk",
    "ChunkType",
    "DocumentMetadata",
    "IngestionError",
    "ScrapingError",
    "ChunkingError",
]
