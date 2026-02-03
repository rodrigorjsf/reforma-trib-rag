"""Custom exceptions for ingestion pipeline."""


class IngestionError(Exception):
    """Base exception for ingestion errors."""
    pass


class ScrapingError(IngestionError):
    """Error during web scraping."""
    pass


class ChunkingError(IngestionError):
    """Error during document chunking."""
    pass


class MetadataExtractionError(IngestionError):
    """Error during metadata extraction."""
    pass
