import pytest
from unittest.mock import Mock, patch
from src.embeddings.ollama_embedder import OllamaEmbedder


@pytest.fixture
def mock_ollama():
    """Mock ollama responses"""
    with patch('ollama.list'), patch('ollama.embeddings') as mock_embed:
        mock_embed.return_value = {
            "embedding": [0.1] * 768  # nomic-embed is 768 dims
        }
        yield mock_embed


def test_embedder_initialization():
    """Test embedder initializes with model name"""
    with patch('ollama.list'):
        embedder = OllamaEmbedder(model="nomic-embed-text")
        assert embedder.model == "nomic-embed-text"
        assert embedder.dimensions == 768


def test_embed_single_text(mock_ollama):
    """Test embedding single text"""
    embedder = OllamaEmbedder()
    embedding = embedder.embed("Test text")

    assert len(embedding) == 768
    assert all(isinstance(x, float) for x in embedding)
    mock_ollama.assert_called_once()


def test_embed_batch(mock_ollama):
    """Test batch embedding"""
    embedder = OllamaEmbedder()
    texts = ["Text 1", "Text 2", "Text 3"]
    embeddings = embedder.embed_batch(texts)

    assert len(embeddings) == 3
    assert all(len(emb) == 768 for emb in embeddings)
    assert mock_ollama.call_count == 3


def test_embed_empty_text(mock_ollama):
    """Test embedding empty text raises error"""
    embedder = OllamaEmbedder()

    with pytest.raises(ValueError, match="Cannot embed empty text"):
        embedder.embed("")
