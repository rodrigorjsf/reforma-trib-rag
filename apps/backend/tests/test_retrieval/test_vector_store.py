import pytest
import tempfile
import shutil
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional
from src.retrieval.vector_store import VectorStore


class ChunkType(Enum):
    """Chunk type enumeration for testing"""
    ARTICLE = "article"
    PARAGRAPH = "paragraph"


@dataclass
class LegalChunk:
    """Legal chunk dataclass for testing"""
    text: str
    source_id: str
    artigo: str
    paragrafo: Optional[str]
    inciso: Optional[str]
    chunk_type: ChunkType
    token_count: int
    metadata: Dict


@pytest.fixture
def temp_db_path():
    """Create temporary directory for ChromaDB"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def vector_store(temp_db_path):
    """Create VectorStore with temporary database"""
    return VectorStore(persist_dir=temp_db_path)


@pytest.fixture
def sample_chunks():
    """Sample legal chunks for testing"""
    return [
        LegalChunk(
            text="Art. 46. A alíquota do CBS será de 7%",
            source_id="LC_214_2024",
            artigo="Art. 46",
            paragrafo=None,
            inciso=None,
            chunk_type=ChunkType.ARTICLE,
            token_count=15,
            metadata={"url": "https://example.com"}
        ),
        LegalChunk(
            text="§ 1º A alíquota pode ser reduzida até 3,5%",
            source_id="LC_214_2024",
            artigo="Art. 46",
            paragrafo="§1º",
            inciso=None,
            chunk_type=ChunkType.PARAGRAPH,
            token_count=12,
            metadata={"url": "https://example.com"}
        )
    ]


def test_vector_store_initialization(vector_store):
    """Test VectorStore initializes correctly"""
    assert vector_store.collection is not None
    assert vector_store.collection.name == "legal_documents"


def test_add_chunks(vector_store, sample_chunks):
    """Test adding chunks to vector store"""
    # Create dummy embeddings (768 dims)
    embeddings = [[0.1] * 768, [0.2] * 768]

    vector_store.add_chunks(sample_chunks, embeddings)

    # Verify chunks were added
    count = vector_store.collection.count()
    assert count == 2


def test_search_by_embedding(vector_store, sample_chunks):
    """Test searching by query embedding"""
    embeddings = [[0.1] * 768, [0.2] * 768]
    vector_store.add_chunks(sample_chunks, embeddings)

    # Search with query embedding
    query_embedding = [0.15] * 768  # Similar to first chunk
    results = vector_store.search(query_embedding, top_k=1)

    assert len(results) == 1
    assert "Art. 46" in results[0]["text"]


def test_delete_by_source(vector_store, sample_chunks):
    """Test deleting chunks by source_id"""
    embeddings = [[0.1] * 768, [0.2] * 768]
    vector_store.add_chunks(sample_chunks, embeddings)

    # Delete by source
    vector_store.delete_by_source("LC_214_2024")

    # Verify deletion
    count = vector_store.collection.count()
    assert count == 0
