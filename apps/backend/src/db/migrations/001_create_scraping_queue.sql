-- apps/backend/src/db/migrations/001_create_scraping_queue.sql
CREATE TABLE IF NOT EXISTS scraping_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    legal_reference TEXT UNIQUE NOT NULL,
    source_url TEXT NOT NULL,
    status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'processing', 'completed', 'failed', 'completed_not_indexed')),
    attempts INTEGER DEFAULT 0,
    priority INTEGER DEFAULT 1,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_status_priority ON scraping_queue(status, priority DESC);
CREATE INDEX IF NOT EXISTS idx_legal_reference ON scraping_queue(legal_reference);
