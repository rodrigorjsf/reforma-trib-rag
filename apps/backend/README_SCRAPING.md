# Dynamic Corpus Expansion System

## Overview

The scraping system automatically expands the legal document corpus by detecting citations in user responses and progressively downloading referenced laws.

## Architecture

### Components

1. **Citation Detector** (`src/agents/citation_detector.py`)
   - Extracts legal references from LLM responses using regex
   - Extracts references from RAG chunk metadata
   - Normalizes to standard format (LC-227-2026, CF-art-156A, etc.)

2. **Queue Manager** (`src/agents/queue_manager.py`)
   - SQLite-based job queue with priority support
   - Deduplication and priority increment for repeated citations
   - Status tracking (pending, processing, completed, failed)

3. **Scraping Worker** (`src/agents/scraping_worker.py`)
   - Background daemon thread
   - Polls queue every 5s (configurable)
   - Scrapes via Firecrawl MCP
   - Saves to `docs/` directory
   - TODO: Indexes in ChromaDB

### Flow

```
User Query → RAG Response → Citation Detector
                                    ↓
                          Extract legal references
                                    ↓
                    Check if already in /docs or queue
                                    ↓
                         Enqueue new references
                                    ↓
                    Background Worker (async)
                                    ↓
                    Scrape → Save → Index → Mark Complete
```

## Configuration

Environment variables in `.env`:

```bash
# Worker
SCRAPING_WORKER_ENABLED=true
SCRAPING_WORKER_POLL_INTERVAL=5
SCRAPING_WORKER_MAX_RETRIES=3

# Queue
QUEUE_DB_PATH=./data/scraping_queue.db

# Firecrawl
FIRECRAWL_TIMEOUT=60
FIRECRAWL_MAX_RETRIES=3

# Storage
DOCS_PATH=./docs
```

## Running

Worker starts automatically with FastAPI:

```bash
uvicorn src.main:app --reload
```

To disable worker:
```bash
SCRAPING_WORKER_ENABLED=false uvicorn src.main:app
```

## Testing

```bash
# Unit tests
pytest tests/agents/ tests/utils/ tests/services/ -v

# Integration tests
pytest tests/integration/ -v

# All tests
pytest -v
```

## Database

Queue stored in SQLite at `./data/scraping_queue.db`

Inspect queue:
```bash
sqlite3 data/scraping_queue.db "SELECT * FROM scraping_queue;"
```

## Monitoring

Check queue status:
```bash
sqlite3 data/scraping_queue.db "
SELECT status, COUNT(*) as count
FROM scraping_queue
GROUP BY status;
"
```

Check recent failures:
```bash
sqlite3 data/scraping_queue.db "
SELECT legal_reference, error_message, updated_at
FROM scraping_queue
WHERE status = 'failed'
ORDER BY updated_at DESC
LIMIT 10;
"
```

## Future Enhancements

- [ ] ChromaDB indexing integration
- [ ] Redis queue backend for production scale
- [ ] Metrics and observability (Prometheus)
- [ ] Admin dashboard for queue management
- [ ] Retry logic for failed jobs
- [ ] Rate limiting for Firecrawl API
