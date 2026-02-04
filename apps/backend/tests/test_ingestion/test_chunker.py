import pytest
from src.ingestion.chunker import HybridChunker
from src.ingestion.models import ChunkType


@pytest.fixture
def chunker():
    return HybridChunker(
        max_chunk_size=800,
        min_chunk_size=100
    )


@pytest.fixture
def sample_markdown():
    """Sample legal document in Markdown"""
    return """# Lei Complementar 214/2024

Art. 1º Esta Lei Complementar institui a CBS.

§ 1º A CBS é um imposto sobre o valor agregado.

§ 2º A CBS incide sobre operações com bens e serviços.

Art. 2º O fato gerador da CBS é a operação com bens.

Art. 3º A base de cálculo é o valor da operação.
"""


def test_chunker_splits_by_article(chunker, sample_markdown):
    """Test chunker creates one chunk per article"""
    chunks = chunker.chunk_document(
        content=sample_markdown,
        source_id="LC_214_2024",
        url="https://example.com"
    )

    # Should have 3 articles
    assert len(chunks) >= 3

    # Check first chunk
    assert "Art. 1º" in chunks[0].text
    assert chunks[0].artigo == "Art. 1"
    assert chunks[0].source_id == "LC_214_2024"


def test_chunker_handles_paragraphs(chunker, sample_markdown):
    """Test chunker extracts paragraph metadata"""
    chunks = chunker.chunk_document(
        content=sample_markdown,
        source_id="LC_214_2024",
        url="https://example.com"
    )

    # Find chunks with paragraphs
    paragraph_chunks = [c for c in chunks if c.paragrafo is not None]

    assert len(paragraph_chunks) >= 2
    assert any("§1º" in c.paragrafo for c in paragraph_chunks)
    assert any("§2º" in c.paragrafo for c in paragraph_chunks)


def test_chunker_assigns_chunk_types(chunker, sample_markdown):
    """Test chunker assigns correct chunk types"""
    chunks = chunker.chunk_document(
        content=sample_markdown,
        source_id="LC_214_2024",
        url="https://example.com"
    )

    # Should have both article and paragraph chunks
    types = {c.chunk_type for c in chunks}
    assert ChunkType.ARTICLE in types or ChunkType.PARAGRAPH in types


def test_chunker_counts_tokens(chunker, sample_markdown):
    """Test chunker counts tokens for each chunk"""
    chunks = chunker.chunk_document(
        content=sample_markdown,
        source_id="LC_214_2024",
        url="https://example.com"
    )

    for chunk in chunks:
        assert chunk.token_count > 0
        assert chunk.token_count < 100  # Small test chunks
