import pytest
from src.ingestion.models import LegalChunk, ChunkType


def test_legal_chunk_creation():
    """Test LegalChunk model creation with all fields"""
    chunk = LegalChunk(
        text="Art. 46. A alíquota do CBS será de 7%",
        source_id="LC_214_2024",
        artigo="Art. 46",
        paragrafo=None,
        inciso=None,
        chunk_type=ChunkType.ARTICLE,
        token_count=15,
        metadata={"url": "https://example.com"}
    )

    assert chunk.artigo == "Art. 46"
    assert chunk.paragrafo is None
    assert chunk.chunk_type == ChunkType.ARTICLE
    assert chunk.source_id == "LC_214_2024"


def test_legal_chunk_with_paragraph():
    """Test LegalChunk with paragraph metadata"""
    chunk = LegalChunk(
        text="§ 1º A alíquota referida...",
        source_id="LC_214_2024",
        artigo="Art. 46",
        paragrafo="§1º",
        inciso=None,
        chunk_type=ChunkType.PARAGRAPH,
        token_count=10,
        metadata={}
    )

    assert chunk.paragrafo == "§1º"
    assert chunk.chunk_type == ChunkType.PARAGRAPH
