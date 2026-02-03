# ReformaTax - RAG Pipeline Design

**Version:** 1.0
**Date:** 2025-02-02
**Status:** Ready for Implementation
**Approach:** Integrated Pipeline Service (Approach 1)

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Architecture Overview](#architecture-overview)
3. [Module Specifications](#module-specifications)
4. [API Design](#api-design)
5. [Error Handling](#error-handling)
6. [Update & Versioning](#update--versioning)
7. [Documentation Requirements](#documentation-requirements)
8. [Implementation Phases](#implementation-phases)

---

## Executive Summary

### Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Architecture | Integrated Pipeline Service | Zero infra overhead, fast MVP iteration, easy debugging |
| Scraping | BeautifulSoup customizado | Zero cost, Planalto HTML is stable, full control |
| Embeddings | Ollama + nomic-embed (local) | Zero per-query cost, multilingual PT-BR support |
| Vector DB | ChromaDB (persistent) | Zero infra, embedded in FastAPI process |
| LLM | Groq + Mixtral-8x7B | Free tier, sub-100ms latency, streaming native |
| Retrieval | RRF (Vector + BM25) | Battle-tested, zero tuning needed, handles keyword mismatch |
| Chunking | Hybrid (respect Art/§) | Preserves legal structure for accurate citations |
| Metadata | Keep § symbol as-is | Legal standard notation in Brazil |

### Core Requirements Met

- ✅ 130+ legal documents from Planalto (HTML scraping)
- ✅ Citation-grounded responses with inline references
- ✅ Dual-prompt system (Generator + Validator)
- ✅ Hybrid search (vector + keyword + RRF)
- ✅ Document update capability (incremental re-indexing)
- ✅ TÉCNICO vs SIMPLIFICADO language modes
- ✅ Zero infrastructure cost (Railway-compatible)

---

## Architecture Overview

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                        FastAPI App                          │
│                       (main.py)                             │
└───────────────┬─────────────────────────────────────────────┘
                │
        ┌───────┴────────┐
        │                │
        ▼                ▼
┌──────────────┐  ┌──────────────┐
│  INGESTION   │  │    QUERY     │
│   MODULE     │  │   MODULE     │
└──────┬───────┘  └──────┬───────┘
       │                 │
       ▼                 ▼
┌────────────────────────────────┐
│  STORAGE LAYER                 │
│  - ChromaDB (vectors)          │
│  - BM25 Index (keywords)       │
│  - Version Registry (updates)  │
└────────────────────────────────┘
```

### Data Flow

**Ingestion Flow:**
```
URL/PDF → Scraper/Parser → Markdown → Chunker →
Metadata Extractor → Embedder → ChromaDB + BM25 Index
```

**Query Flow:**
```
User Question → Vector Search + BM25 Search → RRF Merge →
Top-5 Chunks → Generator Prompt → LLM Response →
Validator Prompt → Decision (OK/WARNING/BLOCKED) → User
```

---

## Module Specifications

### 1. Ingestion Module

**Location:** `apps/backend/src/ingestion/`

#### Structure

```
ingestion/
├── scrapers/
│   ├── planalto_scraper.py    # BeautifulSoup for .htm
│   └── scraper_base.py         # Interface comum
├── parsers/
│   ├── pdf_parser.py           # Marker para PDFs (future)
│   └── html_to_markdown.py     # markdownify wrapper
├── chunker.py                  # Hybrid chunking logic
├── metadata_extractor.py       # Regex for Art/§/Inciso
├── update_manager.py           # Document versioning & updates
└── pipeline.py                 # Orchestrates ingestion
```

#### Planalto Scraper

**Purpose:** Scrape legal documents from planalto.gov.br (130+ URLs)

**Technology:** BeautifulSoup4 + markdownify

**Key Features:**
- Extracts HTML article content
- Converts to clean Markdown
- Extracts metadata (title, law number, date)
- Handles Planalto's consistent HTML structure

**Code Signature:**
```python
def scrape_planalto(url: str) -> dict:
    """
    Returns:
        {
            "source_id": "LC_214_2024",
            "title": "LEI COMPLEMENTAR Nº 214...",
            "content": "# Lei...\n\nArt. 1...",
            "url": "https://...",
            "scraped_at": "2025-02-02T..."
        }
    """
```

#### Hybrid Chunker

**Purpose:** Split legal documents preserving hierarchical structure

**Strategy:**
1. **Default:** 1 article = 1 chunk (if < 800 tokens)
2. **Large articles:** Split by paragraphs (§1º, §2º each a chunk)
3. **Small articles:** Aggregate consecutive articles (if < 100 tokens)

**Metadata Preserved:**
- `artigo`: "Art. 46" (parent article)
- `paragrafo`: "§1º" or None (if caput)
- `inciso`: "I", "II" or None
- `chunk_type`: "article" | "paragraph" | "aggregated"

**Code Signature:**
```python
@dataclass
class LegalChunk:
    text: str
    source_id: str              # "LC_214_2024"
    artigo: str                 # "Art. 46"
    paragrafo: Optional[str]    # "§1º" or None
    inciso: Optional[str]       # "I" or None
    chunk_type: str
    token_count: int
    metadata: dict

def chunk_document(markdown: str, source_id: str) -> list[LegalChunk]:
    """Chunks document preserving legal structure"""
```

**Example Output:**
```python
[
    LegalChunk(
        text="Art. 46. A alíquota do CBS será de sete por cento...",
        artigo="Art. 46",
        paragrafo=None,  # caput
        chunk_type="paragraph"
    ),
    LegalChunk(
        text="§ 1º A alíquota referida no caput...",
        artigo="Art. 46",
        paragrafo="§1º",
        chunk_type="paragraph"
    )
]
```

#### Metadata Extractor

**Purpose:** Extract legal references via regex patterns

**Patterns:**
- Articles: `Art\.\s*(\d+(?:-[A-Z])?)`
- Paragraphs: `§\s*(\d+º)`
- Incisos: `Inciso\s+([IVXLCDM]+)`
- Law numbers: `LC\s*(\d+)/(\d{4})`

**Context Tracking:**
- Maintains `current_article` as parser reads sequentially
- Associates each § with its parent article
- Handles nested structures (Art → § → Inciso → Alínea)

---

### 2. Embeddings Module

**Location:** `apps/backend/src/embeddings/`

#### Ollama Client

**Technology:** Ollama + nomic-embed-text (768 dims)

**Features:**
- Local embedding generation (zero API cost)
- Multilingual support (optimized for PT-BR)
- Batch processing for performance

**Code Signature:**
```python
class OllamaEmbedder:
    def __init__(self, model="nomic-embed-text"):
        self.model = model

    def embed(self, text: str) -> list[float]:
        """Single embedding (768 dims)"""

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Batch embedding for efficiency"""
```

**Setup Requirements:**
- Ollama running on Railway container
- Model pulled: `ollama pull nomic-embed-text`
- Health check: verify Ollama availability on startup

---

### 3. Storage Module

**Location:** `apps/backend/src/retrieval/`

#### ChromaDB Vector Store

**Configuration:**
- **Mode:** Persistent (Railway volume)
- **Distance:** Cosine similarity
- **Collection:** `legal_documents`

**Metadata Schema:**
```python
{
    "source_id": "LC_214_2024",
    "artigo": "Art. 46",
    "paragrafo": "§1º",
    "chunk_type": "paragraph",
    "url": "https://...",
    "indexed_at": "2025-02-02T...",
    "content_hash": "a3f2e1..."  # for version tracking
}
```

**Code Signature:**
```python
class VectorStore:
    def add_chunks(self, chunks: list[LegalChunk], embeddings: list[list[float]])
    def search(self, query_embedding: list[float], top_k=10) -> list[dict]
    def delete_by_source(self, source_id: str)
    def list_all_sources() -> list[dict]
```

#### BM25 Keyword Index

**Technology:** rank-bm25 library

**Purpose:** Keyword search for exact term matching (complements vector search)

**Features:**
- Tokenization: lowercase + split
- Persistence: pickle to disk
- Incremental updates: rebuild index on document add/remove

**Code Signature:**
```python
class BM25Index:
    def add_documents(self, chunks: list[LegalChunk])
    def search(self, query: str, top_k=10) -> list[dict]
    def remove_documents(self, source_id: str)
    def rebuild_index()
```

---

### 4. Retrieval Module

**Location:** `apps/backend/src/retrieval/`

#### Hybrid Search with RRF

**Strategy:** Reciprocal Rank Fusion

**Formula:** `score(doc) = Σ (1 / (k + rank))` where k=60

**Process:**
1. Run vector search → top 10 results
2. Run BM25 search → top 10 results
3. Merge using RRF → combined scores
4. Return top 5 final results

**Code Signature:**
```python
def reciprocal_rank_fusion(
    vector_results: list[dict],
    bm25_results: list[dict],
    k=60
) -> list[dict]:
    """Merge two ranked lists using RRF"""

class QueryEngine:
    def search(self, query: str, top_k=5) -> list[dict]:
        """Executes hybrid search"""
```

**Why RRF:**
- Zero hyperparameter tuning (k=60 is standard)
- Handles keyword mismatch (vector) + exact matches (BM25)
- Battle-tested for legal/regulatory RAG
- Simple to implement and debug

---

### 5. Generation Module

**Location:** `apps/backend/src/generation/`

#### Structure

```
generation/
├── groq_client.py           # Groq API wrapper
├── prompts/
│   ├── generator.txt        # System prompt for Generator
│   └── validator.txt        # System prompt for Validator
├── prompt_builder.py        # Variable injection
└── pipeline.py              # Generator → Validator flow
```

#### Groq Client

**Technology:** Groq API + Mixtral-8x7B-32768

**Configuration:**
- **Generator:** temperature=0.1, max_tokens=800
- **Validator:** temperature=0.0, max_tokens=1500, JSON mode

**Code Signature:**
```python
class GroqClient:
    def generate(self, system_prompt: str, temperature=0.1, max_tokens=800) -> str
    def validate(self, system_prompt: str) -> dict  # Returns JSON
```

#### Dual-Prompt System

**Generator Prompt:**
- Role: Create citation-grounded responses
- Input: Context chunks + user question + mode (TÉCNICO/SIMPLIFICADO)
- Output: Response with inline citations `[Art. X, §Y — LC Z/AAAA]`
- Fallback: Returns explicit "not found" if context insufficient

**Validator Prompt:**
- Role: Verify response against acceptance criteria
- Input: Context + question + generated response + mode
- Output: JSON with verdict (PASS/FAIL), severity (OK/AVISO/CRITICO)
- Process: Decomposes response into atomic claims, verifies each against context

**Decision Logic:**
- **CRITICO** → Block response, return fallback message
- **AVISO** → Send response with warning flag to frontend
- **OK** → Send response normally

**Prompt Files:**
- Copy from `docs/ReformaTax_System_Prompts.md` sections 2 & 3
- Store in `apps/backend/src/generation/prompts/`
- Load at runtime (allows updates without code redeploy)

#### Language Modes

**TÉCNICO:**
- Uses precise legal terminology
- Terms: "caput", "inciso", "alínea", "supracitado"
- Audience: Accountants, lawyers, fiscal professionals

**SIMPLIFICADO:**
- Plain Portuguese, no jargon
- Explains legal terms in accessible language
- **Always keeps citations** (never removed)
- Audience: MEIs, small business owners, general public

---

### 6. Update & Versioning Module

**Location:** `apps/backend/src/ingestion/update_manager.py`

#### Purpose

Handle ongoing tax reform updates:
- New regulations published weekly
- Amendments to existing laws
- Revoked/superseded documents

#### Update Strategy

**1. Content Hash Tracking**
- SHA256 hash of document content
- Stored with each document version
- Enables change detection without re-downloading

**2. Incremental Re-indexing**
- Detect changes via hash comparison
- Remove old chunks for modified source
- Re-process and index only changed documents
- Preserve unchanged documents

**3. Version Registry**
```python
@dataclass
class DocumentVersion:
    source_id: str
    url: str
    content_hash: str
    last_updated: datetime
    chunk_count: int
    status: str  # "active" | "superseded"
```

**Code Signature:**
```python
class UpdateManager:
    def check_for_updates(self, url: str) -> dict:
        """Returns: {"status": "new"|"unchanged"|"modified", "action": ...}"""

    def update_document(self, url: str) -> dict:
        """Re-ingests if modified, skips if unchanged"""

    def refresh_all_sources() -> dict:
        """Checks all 130+ documents, updates modified ones"""
```

#### Automated Refresh

**Strategy:** Weekly cron job (Railway cron or scheduled task)

**Schedule:** Every Monday at 3am UTC

**Process:**
1. Iterate through all indexed sources
2. Check each URL for changes (hash comparison)
3. Re-ingest modified documents
4. Log results (updated/unchanged counts)
5. Alert if failures

---

## API Design

**Location:** `apps/backend/src/main.py`

### Endpoints

#### POST `/api/query`

**Purpose:** Answer questions about tax reform

**Request:**
```json
{
  "question": "Qual é a alíquota do CBS?",
  "mode": "SIMPLIFICADO",
  "user_id": "optional"
}
```

**Response:**
```json
{
  "status": "OK",
  "response": "A alíquota do CBS é de 7% [Art. 46, caput — LC 214/2024].",
  "sources": [
    {
      "source_id": "LC_214_2024",
      "artigo": "Art. 46",
      "paragrafo": null,
      "text": "Art. 46. A alíquota do CBS...",
      "url": "https://..."
    }
  ],
  "warnings": null,
  "validation_summary": "Resposta aprovada - todas as citações verificadas."
}
```

**Status Values:**
- `OK`: Clean response, all validations passed
- `WARNING`: Response sent but has minor issues
- `BLOCKED`: Response blocked due to critical validation failure

---

#### POST `/api/ingest`

**Purpose:** Ingest new document (admin only)

**Request:**
```json
{
  "url": "https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp214.htm",
  "source_type": "html"
}
```

**Response:**
```json
{
  "status": "success",
  "chunks_indexed": 247,
  "source_id": "LC_214_2024",
  "message": "Documento indexado com sucesso"
}
```

---

#### POST `/api/update/{source_id}`

**Purpose:** Re-ingest specific document if modified

**Response:**
```json
{
  "source_id": "LC_214_2024",
  "status": "updated",
  "message": "Documento atualizado com sucesso",
  "chunks_updated": 15
}
```

---

#### POST `/api/refresh-all`

**Purpose:** Check all documents and update modified ones (cron job)

**Response:**
```json
{
  "total_sources": 130,
  "updated": ["LC_214_2024", "DECRETO_123_2025"],
  "unchanged": ["LC_227_2026", ...],
  "timestamp": "2025-02-02T03:00:00Z"
}
```

---

#### GET `/health`

**Purpose:** System health check

**Response:**
```json
{
  "status": "healthy",
  "components": {
    "ollama": "ok",
    "chromadb": "ok",
    "groq": "ok"
  }
}
```

**Status Values:**
- `healthy`: All components OK
- `degraded`: Some components down but system functional
- `unhealthy`: Critical components down

---

#### GET `/api/sources`

**Purpose:** List all indexed documents

**Response:**
```json
{
  "sources": [
    {
      "source_id": "LC_214_2024",
      "title": "Lei Complementar 214/2024",
      "chunk_count": 247,
      "last_updated": "2025-02-02T10:00:00Z",
      "url": "https://..."
    }
  ]
}
```

---

#### GET `/api/sources/{source_id}/version`

**Purpose:** Get version info for specific document

**Response:**
```json
{
  "source_id": "LC_214_2024",
  "last_updated": "2025-02-02T10:00:00Z",
  "chunk_count": 247,
  "content_hash": "a3f2e1bc...",
  "status": "active"
}
```

---

## Error Handling

### Error Categories

#### 1. Ingestion Errors

| Error | Cause | Handling |
|-------|-------|----------|
| Network timeout | URL unreachable | Retry 3x with backoff, then fail with clear message |
| HTML malformed | Planalto structure changed | Log error, alert admin, skip document |
| No chunks generated | Empty/invalid document | Raise IngestionError with details |
| Embedding failure | Ollama offline | Fail ingestion, require manual retry after Ollama fix |

**Code Pattern:**
```python
try:
    doc = scraper.scrape(url)
except requests.RequestException as e:
    raise IngestionError(f"Network error: {e}")
```

---

#### 2. Retrieval Errors

| Error | Cause | Handling |
|-------|-------|----------|
| No results found | Query too specific | Return empty list → triggers generator fallback |
| Vector search fails | ChromaDB offline | Fallback to BM25-only search |
| BM25 search fails | Index corrupted | Fallback to vector-only search |
| Both searches fail | System degraded | Return error to user, log incident |

**Graceful Degradation:**
- If vector fails → use BM25 only
- If BM25 fails → use vector only
- If both fail → return service unavailable

---

#### 3. Generation Errors

| Error | Cause | Handling |
|-------|-------|----------|
| Groq API rate limit | Free tier exceeded | Retry with exponential backoff (3 attempts) |
| Groq timeout | Network issue | Retry, then return cached response if available |
| Invalid response | LLM hallucination | Validator catches → blocks response |
| Validation JSON error | Validator output malformed | Log warning, assume PASS (better than blocking) |

**Retry Logic:**
```python
@retry(max_attempts=3, backoff=exponential)
def generate_response(prompt):
    return groq.generate(prompt)
```

---

#### 4. Edge Cases

| Edge Case | Detection | Handling |
|-----------|-----------|----------|
| Document without articles | Chunker returns 0 chunks | Fail ingestion with clear error |
| Query in English | Language detection | Return: "Por favor, faça perguntas em português" |
| Fabricated citation | Validator check | Severity=CRITICO → block response |
| Context insufficient | Retrieval returns < 2 chunks | Generator uses fallback protocol |

---

## Update & Versioning

### Weekly Refresh Process

**Trigger:** Cron job every Monday 3am UTC

**Steps:**
1. Fetch list of all indexed sources (130+ URLs)
2. For each source:
   - Download current content
   - Compute SHA256 hash
   - Compare with stored hash
   - If different → re-ingest
   - If same → skip
3. Log results:
   - Updated sources count
   - Unchanged sources count
   - Failed sources (if any)
4. Send summary to admin (email/Slack)

**Performance:**
- ~130 documents
- Hash check: ~1 second per document
- Full re-ingest: ~2-3 minutes per document
- Expected updates: 5-10 documents per week
- Total time: ~30 minutes weekly

---

### Manual Update Workflow

**Scenario:** User reports outdated information

**Process:**
1. Admin identifies source_id (e.g., "LC_214_2024")
2. Calls `POST /api/update/LC_214_2024`
3. System:
   - Fetches latest content from URL
   - Compares hash
   - Re-ingests if changed
   - Returns update status
4. Admin verifies via `/api/sources/LC_214_2024/version`

---

### Version Metadata

**Stored in version registry:**
```python
{
  "LC_214_2024": {
    "url": "https://www.planalto.gov.br/...",
    "content_hash": "a3f2e1bc8d4f...",
    "last_updated": "2025-02-02T10:00:00Z",
    "chunk_count": 247,
    "status": "active"
  }
}
```

**Displayed in UI:**
```tsx
<div className="freshness-badge">
  📅 Fontes atualizadas: 02/02/2025
</div>
```

---

## Documentation Requirements

> **CRITICAL:** All implementation MUST include both technical and business documentation

### Documentation Standards

**Every module/feature implemented MUST have:**

1. **Technical Documentation**
   - Code comments (docstrings for all public functions/classes)
   - API documentation (OpenAPI/Swagger auto-generated + examples)
   - Architecture diagrams (when introducing new components)
   - Configuration guide (environment variables, setup steps)

2. **Business Documentation**
   - Feature description (what it does, why it exists)
   - User impact (how it helps Carlos/Ana personas)
   - Success metrics (how to measure if it works)
   - Known limitations (what it doesn't do)

3. **Progress Tracking**
   - Implementation status (pending/in-progress/completed)
   - Blockers/dependencies (what's needed to proceed)
   - Test results (unit tests, integration tests, manual QA)
   - Deployment notes (how to deploy, rollback procedure)

---

### Documentation Locations

```
docs/
├── plans/                          # Design documents (this file)
├── technical/
│   ├── api-reference.md            # Auto-generated + manual examples
│   ├── architecture.md             # System diagrams + explanations
│   ├── database-schema.md          # ChromaDB collections, metadata structure
│   └── deployment-guide.md         # How to deploy to Railway
├── business/
│   ├── feature-changelog.md        # What's been built, when, why
│   ├── user-facing-changes.md      # Changes that affect end users
│   └── metrics-dashboard.md        # Success metrics tracking
└── development/
    ├── setup-guide.md              # How to run locally
    ├── testing-guide.md            # How to test each module
    └── troubleshooting.md          # Common issues + solutions
```

---

### Documentation Workflow

**For each implementation phase:**

1. **Before coding:**
   - Update `docs/business/feature-changelog.md` with planned feature
   - Mark status as `in-progress`

2. **During coding:**
   - Write inline docstrings as you code
   - Add comments for complex logic
   - Update architecture diagrams if structure changes

3. **After coding:**
   - Update `docs/technical/api-reference.md` if API changed
   - Add entry to `docs/development/testing-guide.md` with test cases
   - Mark feature as `completed` in changelog
   - Document any deviations from original plan

4. **After testing:**
   - Update `docs/business/metrics-dashboard.md` with results
   - Add troubleshooting notes if issues found
   - Document workarounds for known issues

---

### Required Documentation for Each Module

#### Ingestion Module
- **Technical:** `docs/technical/ingestion-pipeline.md`
  - Scraping logic (how BeautifulSoup extracts content)
  - Chunking algorithm (detailed examples)
  - Metadata extraction regex patterns
- **Business:** Entry in `feature-changelog.md`
  - "Automated ingestion of 130+ Planalto documents"
  - Impact: Eliminates manual data entry
  - Metric: Time to index full corpus

#### Retrieval Module
- **Technical:** `docs/technical/hybrid-search.md`
  - RRF algorithm explanation
  - Vector vs BM25 trade-offs
  - Performance benchmarks
- **Business:** Entry in `feature-changelog.md`
  - "Hybrid search reduces missed queries by 40%"
  - Impact: Better recall on technical terms
  - Metric: Query relevance score

#### Generation Module
- **Technical:** `docs/technical/dual-prompt-system.md`
  - Generator prompt engineering notes
  - Validator rubric explanation
  - Decision logic flow diagram
- **Business:** Entry in `feature-changelog.md`
  - "Citation validation catches 98% of hallucinations"
  - Impact: Zero fabricated legal citations
  - Metric: Hallucination rate

#### Update Module
- **Technical:** `docs/technical/versioning-system.md`
  - Hash-based change detection
  - Incremental re-indexing process
  - Cron job configuration
- **Business:** Entry in `feature-changelog.md`
  - "Weekly auto-updates keep data fresh"
  - Impact: Users always see latest regulations
  - Metric: Update lag time

---

### Progress Tracking Template

**Location:** `docs/development/implementation-progress.md`

```markdown
# Implementation Progress

## Phase 1: Ingestion Module
- [x] BeautifulSoup scraper - Completed 2025-02-03 by @dev
  - Tests: 15/15 passing
  - Coverage: 92%
  - Docs: technical/ingestion-pipeline.md
- [x] Hybrid chunker - Completed 2025-02-04 by @dev
  - Tests: 20/20 passing
  - Edge cases: handled 8/8
  - Docs: technical/chunking-algorithm.md
- [ ] PDF parser (Marker) - Pending (Phase 2)
  - Blocker: Waiting for Marker setup on Railway
  - Estimated: 2 days

## Phase 2: Retrieval Module
- [in-progress] ChromaDB integration - Started 2025-02-05 by @dev
  - Tests: 5/12 passing
  - Blocker: None
  - ETA: 2025-02-06
- [ ] BM25 index - Pending
- [ ] RRF merger - Pending

...
```

---

### Code Documentation Standards

**Required for all public functions:**

```python
def chunk_document(markdown: str, source_id: str) -> list[LegalChunk]:
    """
    Chunks a legal document preserving hierarchical structure.

    Strategy:
    - Articles < 800 tokens: kept as single chunk
    - Articles > 800 tokens: split by paragraphs (§)
    - Articles < 100 tokens: aggregated with next article

    Args:
        markdown: Document content in Markdown format
        source_id: Unique identifier (e.g., "LC_214_2024")

    Returns:
        List of LegalChunk objects with metadata (artigo, paragrafo, etc.)

    Raises:
        ChunkingError: If document has no recognizable structure

    Example:
        >>> chunks = chunk_document(markdown, "LC_214_2024")
        >>> chunks[0].artigo
        'Art. 46'
        >>> chunks[0].paragrafo
        None  # caput

    Business Context:
        Preserving legal structure enables accurate citations in responses,
        which is critical for user trust (PRD success metric: 100% citation rate).

    See Also:
        - docs/technical/chunking-algorithm.md
        - metadata_extractor.py for regex patterns
    """
```

---

### API Documentation Standards

**Every endpoint requires:**

1. **Auto-generated OpenAPI spec** (FastAPI does this automatically)
2. **Manual examples** in `docs/technical/api-reference.md`:

```markdown
## POST /api/query

**Business Purpose:** Answer user questions with citation-grounded responses

**Example Request:**
\`\`\`bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Qual é a alíquota do CBS?",
    "mode": "SIMPLIFICADO"
  }'
\`\`\`

**Example Response (Success):**
\`\`\`json
{
  "status": "OK",
  "response": "A alíquota do CBS é de 7%...",
  "sources": [...]
}
\`\`\`

**Example Response (Blocked - insufficient context):**
\`\`\`json
{
  "status": "BLOCKED",
  "response": "Não foi possível encontrar informação suficiente...",
  "validation": {...}
}
\`\`\`

**Error Scenarios:**
- 500: Groq API unavailable → retry or use cached response
- 422: Invalid question (< 5 chars) → clear error message

**Metrics:**
- Target latency: < 2 seconds (P95)
- Hallucination rate: < 2% (validated by Validator prompt)
```

---

## Implementation Phases

### Phase 1: Ingestion Module (5-7 days)

**Goal:** Scrape & index 130+ legal documents

**Tasks:**
1. Implement BeautifulSoup scraper for Planalto
2. Build hybrid chunker with Art/§ awareness
3. Create metadata extractor (regex patterns)
4. Integrate Ollama embedder
5. Setup ChromaDB persistent storage
6. Build BM25 index

**Deliverables:**
- ✅ Code in `apps/backend/src/ingestion/`
- ✅ Tests: `tests/test_ingestion.py` (unit + integration)
- ✅ Docs: `docs/technical/ingestion-pipeline.md`
- ✅ Docs: Entry in `docs/business/feature-changelog.md`
- ✅ Progress: Update `docs/development/implementation-progress.md`

**Success Criteria:**
- Can ingest 130 documents in < 30 minutes
- Chunking preserves legal structure (manual spot-check)
- Metadata extraction catches 95%+ of Art/§ references

**Documentation Requirements:**
- Document scraping logic (HTML selectors used)
- Document chunking algorithm with examples
- List all regex patterns used for metadata extraction
- Record edge cases encountered during testing

---

### Phase 2: Retrieval Module (3-4 days)

**Goal:** Hybrid search with RRF

**Tasks:**
1. Implement vector search wrapper for ChromaDB
2. Implement BM25 search wrapper
3. Build RRF merger
4. Create QueryEngine orchestrator
5. Add caching layer (optional - if time permits)

**Deliverables:**
- ✅ Code in `apps/backend/src/retrieval/`
- ✅ Tests: `tests/test_retrieval.py`
- ✅ Docs: `docs/technical/hybrid-search.md`
- ✅ Benchmark: Document retrieval quality metrics
- ✅ Progress: Update implementation tracker

**Success Criteria:**
- Retrieval returns relevant results for 90%+ of test queries
- RRF merging improves recall vs. vector-only (A/B test)
- Query latency < 500ms (P95)

**Documentation Requirements:**
- Explain RRF algorithm with example
- Compare vector-only vs. hybrid search results (metrics)
- Document fallback behavior when one search fails
- Record retrieval quality benchmarks

---

### Phase 3: Generation Module (4-5 days)

**Goal:** Dual-prompt system (Generator + Validator)

**Tasks:**
1. Setup Groq client wrapper
2. Copy Generator prompt from docs to `prompts/generator.txt`
3. Copy Validator prompt from docs to `prompts/validator.txt`
4. Build prompt builder (variable injection)
5. Implement generation pipeline with decision logic
6. Add fallback message generation

**Deliverables:**
- ✅ Code in `apps/backend/src/generation/`
- ✅ Prompts in `apps/backend/src/generation/prompts/`
- ✅ Tests: `tests/test_generation.py` (mock Groq responses)
- ✅ Docs: `docs/technical/dual-prompt-system.md`
- ✅ Manual QA: Test 20+ real questions, record hallucination rate
- ✅ Progress: Update tracker

**Success Criteria:**
- 100% of responses include citations (validated by regex check)
- Hallucination rate < 2% (manual audit of 50 responses)
- Validator correctly blocks fabricated citations (test with known bad responses)
- TÉCNICO vs SIMPLIFICADO modes produce distinct language styles

**Documentation Requirements:**
- Document prompt engineering decisions (why each rule exists)
- Record validation rubric examples (good vs. bad responses)
- List all decision logic branches (OK/WARNING/BLOCKED)
- Document fallback message templates

---

### Phase 4: API Integration (2-3 days)

**Goal:** Wire everything into FastAPI

**Tasks:**
1. Create Pydantic models for request/response
2. Implement `/api/query` endpoint
3. Implement `/api/ingest` endpoint
4. Implement `/health` endpoint
5. Add CORS middleware
6. Setup lifespan events (initialize components on startup)

**Deliverables:**
- ✅ Code in `apps/backend/src/main.py` & `models.py`
- ✅ Tests: `tests/test_api.py` (use FastAPI TestClient)
- ✅ Docs: `docs/technical/api-reference.md` (OpenAPI + examples)
- ✅ Postman collection or cURL examples
- ✅ Progress: Update tracker

**Success Criteria:**
- All endpoints return correct status codes (200/422/500)
- Error responses include clear messages
- OpenAPI spec auto-generated and accessible at `/docs`
- End-to-end test: question → response with citations

**Documentation Requirements:**
- Document all endpoints with examples (request/response)
- List all error scenarios and how they're handled
- Document environment variables required
- Create setup guide for running locally

---

### Phase 5: Update & Versioning (2-3 days)

**Goal:** Document update system

**Tasks:**
1. Implement UpdateManager class
2. Add content hash tracking
3. Build incremental re-indexing logic
4. Create `/api/update/{source_id}` endpoint
5. Create `/api/refresh-all` endpoint
6. Setup cron job (Railway cron or scheduled task)

**Deliverables:**
- ✅ Code in `apps/backend/src/ingestion/update_manager.py`
- ✅ Tests: `tests/test_updates.py`
- ✅ Docs: `docs/technical/versioning-system.md`
- ✅ Docs: Cron job configuration guide
- ✅ Progress: Update tracker

**Success Criteria:**
- Hash comparison correctly detects document changes
- Re-indexing replaces old chunks without duplicates
- Weekly refresh completes in < 1 hour
- Manual update endpoint works for single document

**Documentation Requirements:**
- Document hash-based change detection logic
- Explain incremental re-indexing process (why it's safe)
- Document cron job setup on Railway
- Record update performance metrics (time per document)

---

### Phase 6: Testing & Deployment (3-4 days)

**Goal:** Production-ready system

**Tasks:**
1. Write integration tests (end-to-end flows)
2. Perform manual QA (50+ real questions)
3. Measure hallucination rate
4. Load testing (concurrent queries)
5. Setup Railway deployment
6. Configure environment variables
7. Deploy to production
8. Monitor initial usage

**Deliverables:**
- ✅ Tests: `tests/integration/` (full pipeline tests)
- ✅ QA Report: `docs/business/qa-results.md`
- ✅ Deployment: Railway production URL
- ✅ Docs: `docs/technical/deployment-guide.md`
- ✅ Docs: `docs/development/troubleshooting.md`
- ✅ Monitoring: Setup Sentry error tracking
- ✅ Final update: `docs/development/implementation-progress.md`

**Success Criteria:**
- All integration tests pass
- Hallucination rate < 2% (50 question audit)
- System handles 10 concurrent queries without errors
- Deployment successful, health check returns "healthy"
- Error monitoring active (Sentry catching errors)

**Documentation Requirements:**
- Document deployment process step-by-step
- Record QA test results (questions tested, pass/fail)
- Document monitoring setup (Sentry, logs)
- Create troubleshooting guide (common issues + fixes)
- Final business summary: what was built, what works, what's next

---

## Next Steps

1. **Review this design document** - Ensure all stakeholders agree
2. **Create implementation plan** - Use `superpowers:writing-plans` skill
3. **Setup git worktree** - Isolate implementation work
4. **Begin Phase 1** - Start with ingestion module
5. **Document as you go** - Update progress tracker daily

---

**Document Status:** Ready for Implementation
**Estimated Total Time:** 20-25 days (full-time development)
**Next Action:** Create detailed implementation plan with tasks

