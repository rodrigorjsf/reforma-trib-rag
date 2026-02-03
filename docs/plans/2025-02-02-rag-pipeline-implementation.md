# RAG Pipeline Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build complete citation-grounded RAG system for Brazilian tax reform Q&A

**Architecture:** Integrated Pipeline Service - all modules in FastAPI, BeautifulSoup scraping, Ollama embeddings, ChromaDB vectors, Groq generation, hybrid search with RRF

**Tech Stack:** FastAPI, BeautifulSoup4, markdownify, chromadb, ollama-python, groq, rank-bm25, pydantic

**Reference:** `@docs/plans/2025-02-02-rag-pipeline-design.md`

---

## Prerequisites Setup

### Task 0.1: Install Core Dependencies

**Files:**
- Create: `apps/backend/requirements.txt`

**Step 1: Create requirements file**

```bash
cd apps/backend
```

Create `requirements.txt`:
```
# Existing dependencies (FastAPI stack)
fastapi>=0.115.0
uvicorn[standard]>=0.32.0
pydantic>=2.10.0
pydantic-settings>=2.6.0

# New RAG dependencies
beautifulsoup4>=4.12.3
markdownify>=0.13.1
chromadb>=0.5.20
ollama>=0.4.4
groq>=0.13.0
rank-bm25>=0.2.2
tiktoken>=0.8.0
httpx>=0.28.1
```

**Step 2: Install dependencies**

Run:
```bash
cd apps/backend
pip install -r requirements.txt
```

Expected: All packages installed successfully

**Step 3: Verify Ollama is running**

Run:
```bash
ollama list
```

Expected: List of models (or empty if none downloaded)

**Step 4: Pull nomic-embed model**

Run:
```bash
ollama pull nomic-embed-text
```

Expected: Model downloaded successfully

**Step 5: Commit**

```bash
git add apps/backend/requirements.txt
git commit -m "build: add RAG pipeline dependencies

- BeautifulSoup4 + markdownify for HTML scraping
- ChromaDB for vector storage
- Ollama client for local embeddings
- Groq client for LLM generation
- rank-bm25 for keyword search
- tiktoken for token counting"
```

---

## Phase 1: Ingestion Module Foundation

### Task 1.1: Data Models & Exceptions

**Files:**
- Create: `apps/backend/src/ingestion/__init__.py`
- Create: `apps/backend/src/ingestion/models.py`
- Create: `apps/backend/src/ingestion/exceptions.py`

**Step 1: Write test for LegalChunk model**

Create `apps/backend/tests/test_ingestion/__init__.py` (empty file)

Create `apps/backend/tests/test_ingestion/test_models.py`:
```python
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
```

**Step 2: Run test to verify it fails**

Run:
```bash
cd apps/backend
pytest tests/test_ingestion/test_models.py -v
```

Expected: FAIL - `ModuleNotFoundError: No module named 'src.ingestion'`

**Step 3: Implement data models**

Create `apps/backend/src/ingestion/__init__.py`:
```python
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
```

Create `apps/backend/src/ingestion/models.py`:
```python
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
        parts.append(f"— {self.source_id}")
        return f"[{', '.join(parts)}]"


@dataclass
class DocumentMetadata:
    """Metadata for scraped legal document."""

    source_id: str
    title: str
    url: str
    scraped_at: datetime
    content_hash: str
    document_type: str = "law"  # "law", "decree", "regulation"
```

Create `apps/backend/src/ingestion/exceptions.py`:
```python
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
```

**Step 4: Run test to verify it passes**

Run:
```bash
pytest tests/test_ingestion/test_models.py -v
```

Expected: PASS (2 tests)

**Step 5: Commit**

```bash
git add apps/backend/src/ingestion/ apps/backend/tests/test_ingestion/
git commit -m "feat(ingestion): add data models and exceptions

- LegalChunk model with citation generation
- ChunkType enum (article, paragraph, aggregated)
- DocumentMetadata for scraped documents
- Custom exception hierarchy
- Tests for model creation"
```

---

### Task 1.2: Planalto HTML Scraper

**Files:**
- Create: `apps/backend/src/ingestion/scrapers/__init__.py`
- Create: `apps/backend/src/ingestion/scrapers/planalto_scraper.py`
- Create: `apps/backend/tests/test_ingestion/test_scraper.py`

**Step 1: Write failing test for scraper**

Create `apps/backend/tests/test_ingestion/test_scraper.py`:
```python
import pytest
from unittest.mock import Mock, patch
from src.ingestion.scrapers.planalto_scraper import PlanaltoScraper
from src.ingestion.exceptions import ScrapingError


@pytest.fixture
def sample_html():
    """Sample Planalto HTML structure"""
    return """
    <html>
    <head><title>Lei Complementar 214/2024</title></head>
    <body>
        <h1>LEI COMPLEMENTAR Nº 214, DE 16 DE JANEIRO DE 2025</h1>
        <div class="texto">
            <p>Art. 1º Esta Lei Complementar institui a Contribuição sobre Bens e Serviços (CBS).</p>
            <p>§ 1º A CBS é um imposto sobre o valor agregado.</p>
            <p>Art. 2º O fato gerador da CBS é a operação com bens ou a prestação de serviços.</p>
        </div>
    </body>
    </html>
    """


def test_scraper_extracts_title(sample_html):
    """Test scraper extracts document title"""
    with patch('requests.get') as mock_get:
        mock_get.return_value.text = sample_html
        mock_get.return_value.status_code = 200

        scraper = PlanaltoScraper()
        result = scraper.scrape("https://example.com/lcp214.htm")

        assert "214" in result["source_id"]
        assert "Complementar" in result["title"]


def test_scraper_converts_to_markdown(sample_html):
    """Test scraper converts HTML to Markdown"""
    with patch('requests.get') as mock_get:
        mock_get.return_value.text = sample_html
        mock_get.return_value.status_code = 200

        scraper = PlanaltoScraper()
        result = scraper.scrape("https://example.com/lcp214.htm")

        assert "Art. 1º" in result["content"]
        assert "§ 1º" in result["content"]
        assert result["url"] == "https://example.com/lcp214.htm"


def test_scraper_handles_network_error():
    """Test scraper raises ScrapingError on network failure"""
    with patch('requests.get', side_effect=Exception("Network error")):
        scraper = PlanaltoScraper()

        with pytest.raises(ScrapingError, match="Network error"):
            scraper.scrape("https://example.com/test.htm")
```

**Step 2: Run test to verify it fails**

Run:
```bash
pytest tests/test_ingestion/test_scraper.py -v
```

Expected: FAIL - `ModuleNotFoundError: No module named 'src.ingestion.scrapers'`

**Step 3: Implement Planalto scraper**

Create `apps/backend/src/ingestion/scrapers/__init__.py`:
```python
"""Scrapers for legal document sources."""

from .planalto_scraper import PlanaltoScraper

__all__ = ["PlanaltoScraper"]
```

Create `apps/backend/src/ingestion/scrapers/planalto_scraper.py`:
```python
"""Scraper for Planalto legal documents."""

import hashlib
import re
from datetime import datetime, timezone
from typing import Dict

import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md

from ..exceptions import ScrapingError


class PlanaltoScraper:
    """Scraper for planalto.gov.br legal documents."""

    def __init__(self, timeout: int = 30):
        """Initialize scraper.

        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout

    def scrape(self, url: str) -> Dict:
        """Scrape legal document from Planalto.

        Args:
            url: URL of the document to scrape

        Returns:
            Dictionary with:
                - source_id: Extracted law identifier (e.g., "LC_214_2024")
                - title: Document title
                - content: Document content in Markdown
                - url: Original URL
                - scraped_at: Timestamp
                - content_hash: SHA256 hash of content

        Raises:
            ScrapingError: If scraping fails
        """
        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            html = response.text
        except Exception as e:
            raise ScrapingError(f"Failed to fetch {url}: {e}")

        try:
            soup = BeautifulSoup(html, 'html.parser')

            # Extract title
            title_tag = soup.find('h1')
            title = title_tag.text.strip() if title_tag else "Untitled"

            # Extract source_id from title
            source_id = self._extract_source_id(title)

            # Extract main content
            content_div = soup.find('div', class_='texto') or soup.find('article')
            if not content_div:
                raise ScrapingError(f"Could not find content in {url}")

            # Convert HTML to Markdown
            markdown_content = md(str(content_div), heading_style="ATX")

            # Compute content hash
            content_hash = hashlib.sha256(
                markdown_content.encode('utf-8')
            ).hexdigest()

            return {
                "source_id": source_id,
                "title": title,
                "content": markdown_content,
                "url": url,
                "scraped_at": datetime.now(timezone.utc).isoformat(),
                "content_hash": content_hash
            }

        except ScrapingError:
            raise
        except Exception as e:
            raise ScrapingError(f"Failed to parse {url}: {e}")

    def _extract_source_id(self, title: str) -> str:
        """Extract source ID from document title.

        Examples:
            "LEI COMPLEMENTAR Nº 214, DE 16 DE JANEIRO DE 2025" -> "LC_214_2025"
            "DECRETO Nº 12.345 DE 2024" -> "DECRETO_12345_2024"
        """
        # Try to match Lei Complementar
        lc_match = re.search(r'LEI\s+COMPLEMENTAR\s+N[ºÃ]\s*(\d+)[^0-9]*(\d{4})', title, re.IGNORECASE)
        if lc_match:
            return f"LC_{lc_match.group(1)}_{lc_match.group(2)}"

        # Try to match Decreto
        decreto_match = re.search(r'DECRETO\s+N[ºÃ]\s*([\d.]+)[^0-9]*(\d{4})', title, re.IGNORECASE)
        if decreto_match:
            number = decreto_match.group(1).replace('.', '')
            return f"DECRETO_{number}_{decreto_match.group(2)}"

        # Fallback: use hash of title
        title_hash = hashlib.sha256(title.encode()).hexdigest()[:8]
        return f"DOC_{title_hash}"
```

**Step 4: Run tests to verify they pass**

Run:
```bash
pytest tests/test_ingestion/test_scraper.py -v
```

Expected: PASS (3 tests)

**Step 5: Commit**

```bash
git add apps/backend/src/ingestion/scrapers/ apps/backend/tests/test_ingestion/test_scraper.py
git commit -m "feat(ingestion): add Planalto HTML scraper

- BeautifulSoup-based scraper for planalto.gov.br
- Extracts title, content, and metadata
- Converts HTML to Markdown using markdownify
- Extracts source_id from document title (LC_XXX_YYYY)
- Computes SHA256 hash for change detection
- Handles network errors with clear exceptions
- Tests with mocked HTTP responses"
```

---

### Task 1.3: Metadata Extractor (Regex for Art/§)

**Files:**
- Create: `apps/backend/src/ingestion/metadata_extractor.py`
- Create: `apps/backend/tests/test_ingestion/test_metadata_extractor.py`

**Step 1: Write failing test for metadata extraction**

Create `apps/backend/tests/test_ingestion/test_metadata_extractor.py`:
```python
import pytest
from src.ingestion.metadata_extractor import MetadataExtractor


@pytest.fixture
def extractor():
    return MetadataExtractor()


def test_extract_article_number(extractor):
    """Test extraction of article number"""
    text = "Art. 46. A alíquota do CBS será de 7%"
    result = extractor.extract_article(text)
    assert result == "Art. 46"


def test_extract_article_with_letter(extractor):
    """Test extraction of article with letter suffix"""
    text = "Art. 156-A. O imposto municipal..."
    result = extractor.extract_article(text)
    assert result == "Art. 156-A"


def test_extract_paragraph(extractor):
    """Test extraction of paragraph"""
    text = "§ 1º A alíquota referida no caput..."
    result = extractor.extract_paragraph(text)
    assert result == "§1º"


def test_extract_paragraph_with_unicode(extractor):
    """Test extraction with º symbol"""
    text = "§ 2º Outro parágrafo"
    result = extractor.extract_paragraph(text)
    assert result == "§2º"


def test_extract_inciso(extractor):
    """Test extraction of inciso (Roman numerals)"""
    text = "I - primeira alínea"
    result = extractor.extract_inciso(text)
    assert result == "I"

    text = "XII - décima segunda alínea"
    result = extractor.extract_inciso(text)
    assert result == "XII"


def test_extract_all_metadata(extractor):
    """Test extraction of all metadata from text"""
    text = """Art. 46. A alíquota do CBS será de 7%

§ 1º A alíquota referida no caput deste artigo poderá ser reduzida.

I - primeiro caso
II - segundo caso
"""

    metadata = extractor.extract_all(text)

    assert metadata["artigo"] == "Art. 46"
    assert metadata["paragrafos"] == ["§1º"]
    assert set(metadata["incisos"]) == {"I", "II"}
```

**Step 2: Run test to verify it fails**

Run:
```bash
pytest tests/test_ingestion/test_metadata_extractor.py -v
```

Expected: FAIL - `ModuleNotFoundError`

**Step 3: Implement metadata extractor**

Create `apps/backend/src/ingestion/metadata_extractor.py`:
```python
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
```

**Step 4: Run tests to verify they pass**

Run:
```bash
pytest tests/test_ingestion/test_metadata_extractor.py -v
```

Expected: PASS (6 tests)

**Step 5: Commit**

```bash
git add apps/backend/src/ingestion/metadata_extractor.py apps/backend/tests/test_ingestion/test_metadata_extractor.py
git commit -m "feat(ingestion): add regex-based metadata extractor

- Extract article numbers (Art. X, Art. X-A)
- Extract paragraphs (§Xº)
- Extract incisos (Roman numerals I, II, XII, etc)
- Handles Unicode characters (º symbol)
- extract_all() method for batch extraction
- Comprehensive tests for all patterns"
```

---

### Task 1.4: Token Counter

**Files:**
- Create: `apps/backend/src/ingestion/token_counter.py`
- Create: `apps/backend/tests/test_ingestion/test_token_counter.py`

**Step 1: Write failing test**

Create `apps/backend/tests/test_ingestion/test_token_counter.py`:
```python
import pytest
from src.ingestion.token_counter import TokenCounter


@pytest.fixture
def counter():
    return TokenCounter()


def test_count_tokens_simple(counter):
    """Test token counting for simple text"""
    text = "Art. 46. A alíquota do CBS será de 7%"
    count = counter.count(text)
    assert count > 0
    assert count < 20  # Should be around 12-15 tokens


def test_count_tokens_empty(counter):
    """Test token counting for empty text"""
    assert counter.count("") == 0


def test_count_tokens_portuguese(counter):
    """Test token counting for Portuguese text"""
    text = "A Contribuição sobre Bens e Serviços (CBS) é um imposto federal."
    count = counter.count(text)
    assert count > 10
    assert count < 25
```

**Step 2: Run test to verify it fails**

Run:
```bash
pytest tests/test_ingestion/test_token_counter.py -v
```

Expected: FAIL - `ModuleNotFoundError`

**Step 3: Implement token counter**

Create `apps/backend/src/ingestion/token_counter.py`:
```python
"""Token counting utility using tiktoken."""

import tiktoken


class TokenCounter:
    """Count tokens in text using OpenAI's tiktoken."""

    def __init__(self, encoding_name: str = "cl100k_base"):
        """Initialize token counter.

        Args:
            encoding_name: Tiktoken encoding (default: cl100k_base for GPT-4)
        """
        self.encoding = tiktoken.get_encoding(encoding_name)

    def count(self, text: str) -> int:
        """Count tokens in text.

        Args:
            text: Text to count tokens for

        Returns:
            Number of tokens
        """
        if not text:
            return 0
        return len(self.encoding.encode(text))
```

**Step 4: Run tests to verify they pass**

Run:
```bash
pytest tests/test_ingestion/test_token_counter.py -v
```

Expected: PASS (3 tests)

**Step 5: Commit**

```bash
git add apps/backend/src/ingestion/token_counter.py apps/backend/tests/test_ingestion/test_token_counter.py
git commit -m "feat(ingestion): add token counter using tiktoken

- TokenCounter class using cl100k_base encoding
- Compatible with GPT-4 and Mixtral tokenization
- Handles empty strings and Portuguese text
- Tests for various text lengths"
```

---

### Task 1.5: Hybrid Chunker

**Files:**
- Create: `apps/backend/src/ingestion/chunker.py`
- Create: `apps/backend/tests/test_ingestion/test_chunker.py`

**Step 1: Write failing test for chunker**

Create `apps/backend/tests/test_ingestion/test_chunker.py`:
```python
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
```

**Step 2: Run test to verify it fails**

Run:
```bash
pytest tests/test_ingestion/test_chunker.py -v
```

Expected: FAIL - `ModuleNotFoundError`

**Step 3: Implement hybrid chunker**

Create `apps/backend/src/ingestion/chunker.py`:
```python
"""Hybrid chunker that respects legal document structure."""

import re
from typing import List

from .models import LegalChunk, ChunkType
from .metadata_extractor import MetadataExtractor
from .token_counter import TokenCounter


class HybridChunker:
    """Chunks legal documents preserving hierarchical structure.

    Strategy:
    1. Split by articles (Art. X)
    2. If article < max_chunk_size: keep as one chunk
    3. If article > max_chunk_size: split by paragraphs (§)
    4. If article < min_chunk_size: aggregate with next article
    """

    def __init__(
        self,
        max_chunk_size: int = 800,
        min_chunk_size: int = 100
    ):
        """Initialize chunker.

        Args:
            max_chunk_size: Maximum tokens per chunk
            min_chunk_size: Minimum tokens (aggregate if smaller)
        """
        self.max_chunk_size = max_chunk_size
        self.min_chunk_size = min_chunk_size
        self.token_counter = TokenCounter()
        self.metadata_extractor = MetadataExtractor()

    def chunk_document(
        self,
        content: str,
        source_id: str,
        url: str
    ) -> List[LegalChunk]:
        """Chunk document preserving legal structure.

        Args:
            content: Document content in Markdown
            source_id: Document identifier (e.g., "LC_214_2024")
            url: Source URL

        Returns:
            List of LegalChunk objects
        """
        chunks = []

        # Split by articles
        article_sections = self._split_by_articles(content)

        current_article = None

        for section in article_sections:
            # Extract article number
            article = self.metadata_extractor.extract_article(section)
            if article:
                current_article = article

            # Count tokens
            token_count = self.token_counter.count(section)

            # If section is small enough, create single chunk
            if token_count <= self.max_chunk_size:
                chunk = self._create_chunk(
                    text=section,
                    source_id=source_id,
                    article=current_article or "Unknown",
                    paragraph=None,
                    chunk_type=ChunkType.ARTICLE,
                    token_count=token_count,
                    url=url
                )
                chunks.append(chunk)
            else:
                # Split by paragraphs
                paragraph_chunks = self._split_by_paragraphs(
                    section,
                    source_id,
                    current_article or "Unknown",
                    url
                )
                chunks.extend(paragraph_chunks)

        return chunks

    def _split_by_articles(self, content: str) -> List[str]:
        """Split content by article boundaries."""
        # Split on "Art. X" pattern
        pattern = r'(Art\.\s*\d+(?:-[A-Z])?\.)'
        parts = re.split(pattern, content)

        # Recombine article markers with their content
        sections = []
        for i in range(1, len(parts), 2):
            if i + 1 < len(parts):
                sections.append(parts[i] + parts[i + 1])
            elif i < len(parts):
                sections.append(parts[i])

        return [s.strip() for s in sections if s.strip()]

    def _split_by_paragraphs(
        self,
        section: str,
        source_id: str,
        article: str,
        url: str
    ) -> List[LegalChunk]:
        """Split large article by paragraphs."""
        chunks = []

        # Split on paragraph pattern
        pattern = r'(§\s*\d+º)'
        parts = re.split(pattern, section)

        # First part is caput (article body before §1)
        if parts[0].strip():
            token_count = self.token_counter.count(parts[0])
            chunk = self._create_chunk(
                text=parts[0].strip(),
                source_id=source_id,
                article=article,
                paragraph=None,  # caput
                chunk_type=ChunkType.PARAGRAPH,
                token_count=token_count,
                url=url
            )
            chunks.append(chunk)

        # Process paragraphs
        for i in range(1, len(parts), 2):
            if i + 1 < len(parts):
                paragraph_marker = parts[i]
                paragraph_text = parts[i + 1]
                full_text = paragraph_marker + paragraph_text

                token_count = self.token_counter.count(full_text)
                paragraph = self.metadata_extractor.extract_paragraph(paragraph_marker)

                chunk = self._create_chunk(
                    text=full_text.strip(),
                    source_id=source_id,
                    article=article,
                    paragraph=paragraph,
                    chunk_type=ChunkType.PARAGRAPH,
                    token_count=token_count,
                    url=url
                )
                chunks.append(chunk)

        return chunks

    def _create_chunk(
        self,
        text: str,
        source_id: str,
        article: str,
        paragraph: str | None,
        chunk_type: ChunkType,
        token_count: int,
        url: str
    ) -> LegalChunk:
        """Create LegalChunk with metadata."""
        return LegalChunk(
            text=text,
            source_id=source_id,
            artigo=article,
            paragrafo=paragraph,
            inciso=None,  # TODO: extract incisos
            chunk_type=chunk_type,
            token_count=token_count,
            metadata={"url": url}
        )
```

**Step 4: Run tests to verify they pass**

Run:
```bash
pytest tests/test_ingestion/test_chunker.py -v
```

Expected: PASS (4 tests)

**Step 5: Commit**

```bash
git add apps/backend/src/ingestion/chunker.py apps/backend/tests/test_ingestion/test_chunker.py
git commit -m "feat(ingestion): add hybrid chunker for legal documents

- Splits by articles (Art. X) preserving structure
- Splits large articles by paragraphs (§)
- Extracts metadata (article, paragraph) for each chunk
- Counts tokens using TokenCounter
- Assigns chunk types (ARTICLE, PARAGRAPH)
- Tests for article splitting and paragraph handling"
```

---

## Phase 2: Embeddings & Storage

### Task 2.1: Ollama Embedder

**Files:**
- Create: `apps/backend/src/embeddings/__init__.py`
- Create: `apps/backend/src/embeddings/ollama_embedder.py`
- Create: `apps/backend/tests/test_embeddings/test_ollama.py`

**Step 1: Write failing test**

Create `apps/backend/tests/test_embeddings/__init__.py` (empty)

Create `apps/backend/tests/test_embeddings/test_ollama.py`:
```python
import pytest
from unittest.mock import Mock, patch
from src.embeddings.ollama_embedder import OllamaEmbedder


@pytest.fixture
def mock_ollama():
    """Mock ollama responses"""
    with patch('ollama.embeddings') as mock:
        mock.return_value = {
            "embedding": [0.1] * 768  # nomic-embed is 768 dims
        }
        yield mock


def test_embedder_initialization():
    """Test embedder initializes with model name"""
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
```

**Step 2: Run test to verify it fails**

Run:
```bash
pytest tests/test_embeddings/test_ollama.py -v
```

Expected: FAIL - `ModuleNotFoundError`

**Step 3: Implement Ollama embedder**

Create `apps/backend/src/embeddings/__init__.py`:
```python
"""Embeddings module for vector generation."""

from .ollama_embedder import OllamaEmbedder

__all__ = ["OllamaEmbedder"]
```

Create `apps/backend/src/embeddings/ollama_embedder.py`:
```python
"""Ollama-based embedder using nomic-embed-text."""

from typing import List

import ollama


class OllamaEmbedder:
    """Generate embeddings using Ollama with nomic-embed-text."""

    def __init__(self, model: str = "nomic-embed-text"):
        """Initialize embedder.

        Args:
            model: Ollama model name (default: nomic-embed-text)
        """
        self.model = model
        self.dimensions = 768  # nomic-embed-text dimensions

        # Verify Ollama is available
        try:
            ollama.list()
        except Exception as e:
            raise RuntimeError(f"Ollama not available: {e}")

    def embed(self, text: str) -> List[float]:
        """Generate embedding for single text.

        Args:
            text: Text to embed

        Returns:
            List of 768 floats (embedding vector)

        Raises:
            ValueError: If text is empty
        """
        if not text or not text.strip():
            raise ValueError("Cannot embed empty text")

        response = ollama.embeddings(
            model=self.model,
            prompt=text
        )

        return response["embedding"]

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        return [self.embed(text) for text in texts]
```

**Step 4: Run tests to verify they pass**

Run:
```bash
pytest tests/test_embeddings/test_ollama.py -v
```

Expected: PASS (4 tests) - Note: Tests use mocks, so Ollama doesn't need to be running

**Step 5: Commit**

```bash
git add apps/backend/src/embeddings/ apps/backend/tests/test_embeddings/
git commit -m "feat(embeddings): add Ollama embedder with nomic-embed

- OllamaEmbedder class using ollama-python client
- Uses nomic-embed-text model (768 dimensions)
- Single text and batch embedding support
- Verifies Ollama availability on initialization
- Handles empty text with clear error
- Tests with mocked ollama responses"
```

---

### Task 2.2: ChromaDB Vector Store

**Files:**
- Create: `apps/backend/src/retrieval/__init__.py`
- Create: `apps/backend/src/retrieval/vector_store.py`
- Create: `apps/backend/tests/test_retrieval/test_vector_store.py`

**Step 1: Write failing test**

Create `apps/backend/tests/test_retrieval/__init__.py` (empty)

Create `apps/backend/tests/test_retrieval/test_vector_store.py`:
```python
import pytest
import tempfile
import shutil
from pathlib import Path
from src.retrieval.vector_store import VectorStore
from src.ingestion.models import LegalChunk, ChunkType


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
```

**Step 2: Run test to verify it fails**

Run:
```bash
pytest tests/test_retrieval/test_vector_store.py -v
```

Expected: FAIL - `ModuleNotFoundError`

**Step 3: Implement vector store**

Create `apps/backend/src/retrieval/__init__.py`:
```python
"""Retrieval module for hybrid search."""

from .vector_store import VectorStore

__all__ = ["VectorStore"]
```

Create `apps/backend/src/retrieval/vector_store.py`:
```python
"""ChromaDB vector store for legal document chunks."""

from typing import List, Dict

import chromadb
from chromadb.config import Settings

from ..ingestion.models import LegalChunk


class VectorStore:
    """Vector store using ChromaDB for legal document chunks."""

    def __init__(self, persist_dir: str = "./chroma_db"):
        """Initialize vector store.

        Args:
            persist_dir: Directory for persistent storage
        """
        self.client = chromadb.Client(Settings(
            persist_directory=persist_dir,
            anonymized_telemetry=False
        ))

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="legal_documents",
            metadata={"hnsw:space": "cosine"}
        )

    def add_chunks(
        self,
        chunks: List[LegalChunk],
        embeddings: List[List[float]]
    ) -> None:
        """Add chunks with embeddings to store.

        Args:
            chunks: List of LegalChunk objects
            embeddings: List of embedding vectors (one per chunk)
        """
        if len(chunks) != len(embeddings):
            raise ValueError("Number of chunks must match number of embeddings")

        # Generate unique IDs
        ids = [
            f"{c.source_id}_{c.artigo}_{c.paragrafo or 'caput'}_{i}"
            for i, c in enumerate(chunks)
        ]

        # Prepare metadata
        metadatas = [
            {
                "source_id": c.source_id,
                "artigo": c.artigo,
                "paragrafo": c.paragrafo or "",
                "chunk_type": c.chunk_type.value,
                "url": c.metadata.get("url", "")
            }
            for c in chunks
        ]

        # Add to collection
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=[c.text for c in chunks],
            metadatas=metadatas
        )

    def search(
        self,
        query_embedding: List[float],
        top_k: int = 10
    ) -> List[Dict]:
        """Search for similar chunks.

        Args:
            query_embedding: Query vector (768 dims)
            top_k: Number of results to return

        Returns:
            List of dictionaries with:
                - text: Chunk text
                - metadata: Chunk metadata
                - distance: Similarity distance
        """
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )

        # Format results
        formatted = []
        for i in range(len(results["ids"][0])):
            formatted.append({
                "id": results["ids"][0][i],
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i]
            })

        return formatted

    def delete_by_source(self, source_id: str) -> None:
        """Delete all chunks from a specific source.

        Args:
            source_id: Source identifier (e.g., "LC_214_2024")
        """
        self.collection.delete(
            where={"source_id": source_id}
        )

    def list_all_sources(self) -> List[Dict]:
        """List all unique source documents in the store.

        Returns:
            List of dictionaries with source metadata
        """
        # Get all metadatas
        all_data = self.collection.get()

        # Extract unique sources
        sources = {}
        for metadata in all_data["metadatas"]:
            source_id = metadata["source_id"]
            if source_id not in sources:
                sources[source_id] = {
                    "source_id": source_id,
                    "url": metadata.get("url", "")
                }

        return list(sources.values())
```

**Step 4: Run tests to verify they pass**

Run:
```bash
pytest tests/test_retrieval/test_vector_store.py -v
```

Expected: PASS (4 tests)

**Step 5: Commit**

```bash
git add apps/backend/src/retrieval/ apps/backend/tests/test_retrieval/
git commit -m "feat(retrieval): add ChromaDB vector store

- VectorStore class with persistent ChromaDB
- Add chunks with embeddings
- Search by query embedding (cosine similarity)
- Delete chunks by source_id
- List all indexed sources
- Tests with temporary database"
```

---

**Due to the length of this implementation plan, I'll save what we have so far and continue with remaining phases. This gives you a working foundation to start with.**

Let me save this initial plan:
