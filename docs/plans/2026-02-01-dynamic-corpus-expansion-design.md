# Design: Agente de Expansão Dinâmica do Corpus Legal

**Data:** 2026-02-01
**Status:** APROVADO
**Contexto:** ReformaTax - Sistema RAG para consultas sobre reforma tributária brasileira

## Problema

O corpus inicial contém apenas a LCP 214/25, mas esta lei referencia centenas de outras leis, decretos e artigos constitucionais. Usuários fazem perguntas que requerem contexto dessas leis referenciadas, mas fazer scraping de todas antecipadamente seria ineficiente (muitas nunca serão consultadas).

## Solução

Sistema de expansão dinâmica que:
1. Monitora quais leis são citadas nas respostas geradas
2. Verifica se já estão no corpus local
3. Se não estão, agenda scraping em background (não bloqueia resposta)
4. Progressivamente enriquece o corpus baseado em uso real

## Arquitetura

### Componentes Principais

#### 1. Citation Detector

**Responsabilidade:** Identificar referências legais após cada resposta gerada.

**Abordagem Híbrida:**
- **Regex Parser:** Extrai padrões como "Lei nº X/YYYY", "LC X/YYYY", "Art. X da CF"
- **Chunk Tracker:** Extrai campo `legal_references` do metadata dos chunks RAG recuperados
- **Output:** Lista deduplicated e normalizada de referências

**Patterns Regex:**
```python
r'Lei (?:Complementar )?n[º°]?\s*(\d+)[/,]\s*(\d{4})'
r'(?:LC|MP|Decreto)\s*n?[º°]?\s*(\d+)[/,]\s*(\d{4})'
r'Art\.?\s*(\d+[A-Z]?)\s*da\s*(Constituição Federal|CF)'
```

**Normalização:**
- "Lei Complementar nº 227/2026" → `LC-227-2026`
- "Art. 156-A da CF" → `CF-art-156A`
- "Decreto 11.374/2023" → `DEC-11374-2023`

#### 2. Queue Manager

**Responsabilidade:** Gerenciar fila de documentos pendentes de scraping.

**Storage Inicial:** SQLite (migração futura para Redis)

**Schema:**
```sql
CREATE TABLE scraping_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    legal_reference TEXT UNIQUE NOT NULL,
    source_url TEXT NOT NULL,
    status TEXT DEFAULT 'pending',  -- pending, processing, completed, failed
    attempts INTEGER DEFAULT 0,
    priority INTEGER DEFAULT 1,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_status_priority ON scraping_queue(status, priority DESC);
```

**Interface Abstrata:**
```python
class QueueManager(ABC):
    @abstractmethod
    def enqueue(self, ref: LegalReference, url: str, priority: int)

    @abstractmethod
    def get_next_job(self) -> Optional[ScrapingJob]

    @abstractmethod
    def mark_completed(self, job_id: int)

    @abstractmethod
    def mark_failed(self, job_id: int, error: str)
```

**Lógica de Enfileiramento:**
1. Verifica se `/docs/{normalized_ref}.md` já existe → Skip
2. Verifica se já está na fila (status != failed) → Incrementa `priority`
3. Caso contrário: Busca URL em `LCP214-25-SUB-LINKS.md` e cria job

#### 3. Background Worker

**Responsabilidade:** Processar fila de scraping assincronamente.

**Implementação:**
- Thread daemon no processo FastAPI (MVP)
- Poll a cada 5s (configurável)
- Processa jobs por ordem de prioridade decrescente

**Pipeline de Processamento:**
```
get_next_job()
  → scrape_with_firecrawl()
  → save_to_docs()
  → index_in_chromadb()
  → mark_completed()
```

**Retry Logic:**
- Máximo 3 tentativas
- Backoff exponencial: 30s, 60s, 120s
- Após 3 falhas: marca como `failed`, log para revisão manual

## Fluxo de Dados Completo

```
┌─────────────────────────────────────────────────────────────┐
│ 1. User Query Phase                                         │
├─────────────────────────────────────────────────────────────┤
│ Pergunta → Vector Search → Recupera chunks + metadata      │
│ Metadata: {source_document, legal_references: [...]}       │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. Generation Phase                                         │
├─────────────────────────────────────────────────────────────┤
│ LLM gera resposta com citações → Stream ao usuário         │
│ Latência: <30s (não bloqueia)                              │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. Post-Response Analysis (Citation Detection)             │
├─────────────────────────────────────────────────────────────┤
│ Regex Parser: escaneia texto da resposta                   │
│ Chunk Tracker: extrai legal_references do metadata         │
│ Merge + Normalize → Lista de LegalReference objects        │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. Queue Enrichment                                         │
├─────────────────────────────────────────────────────────────┤
│ Para cada referência:                                       │
│   - Já existe em /docs? → Skip                             │
│   - Já na fila? → Incrementa priority                      │
│   - Senão: Resolve URL do SUB-LINKS → Enfileira            │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. Background Processing (Worker Loop)                     │
├─────────────────────────────────────────────────────────────┤
│ Poll fila → Pega job de maior priority                     │
│ Firecrawl scrape → Salva em /docs/{ref}.md                │
│ Indexa no ChromaDB → Marca completed                       │
└─────────────────────────────────────────────────────────────┘
```

## Estrutura de Código

```
apps/backend/src/
├── agents/
│   ├── __init__.py
│   ├── citation_detector.py      # CitationDetector class
│   ├── queue_manager.py           # QueueManager interface + SQLiteQueueManager
│   └── scraping_worker.py         # ScrapingWorker class
├── services/
│   ├── rag_service.py             # Modificar: adicionar chunk tracking
│   └── firecrawl_service.py       # Wrapper para Firecrawl MCP
├── utils/
│   ├── legal_reference_parser.py  # Normalização de referências
│   └── url_resolver.py            # Mapeia referência → URL do SUB-LINKS
└── db/
    ├── migrations/
    │   └── 001_create_scraping_queue.sql
    └── queue_repository.py        # Data Access Layer
```

### Classes Principais

**CitationDetector**
```python
class CitationDetector:
    def detect(
        self,
        response: str,
        retrieved_chunks: List[Chunk]
    ) -> List[LegalReference]:
        """Detecta todas as referências legais na resposta e chunks."""

    def _extract_from_text(self, text: str) -> List[str]:
        """Aplica regex patterns no texto."""

    def _extract_from_chunks(self, chunks: List[Chunk]) -> List[str]:
        """Extrai legal_references do metadata dos chunks."""

    def _normalize(self, raw_refs: List[str]) -> List[LegalReference]:
        """Normaliza para formato padrão (LC-227-2026, etc)."""
```

**ScrapingWorker**
```python
class ScrapingWorker:
    def __init__(self, queue_manager: QueueManager):
        self.queue = queue_manager
        self.firecrawl = FirecrawlService()
        self.poll_interval = int(os.getenv("SCRAPING_WORKER_POLL_INTERVAL", "5"))

    def start(self):
        """Inicia loop de processamento (blocking)."""
        while True:
            job = self.queue.get_next_job()
            if job:
                self._process_job(job)
            time.sleep(self.poll_interval)

    def _process_job(self, job: ScrapingJob):
        """Scrape → Save → Index → Mark completed."""

    def _scrape_document(self, url: str) -> str:
        """Usa Firecrawl MCP para scraping."""

    def _save_and_index(self, content: str, ref: LegalReference):
        """Salva em /docs e indexa no ChromaDB."""
```

## Tratamento de Erros

### Cenários e Mitigações

| Cenário | Mitigação |
|---------|-----------|
| Timeout Firecrawl (>60s) | Retry com backoff exponencial (30s, 60s, 120s) |
| 404/403 no URL | Marca como failed, log para revisão manual |
| Rate limiting Firecrawl | Pausa worker por 5min, tenta novamente |
| HTML malformado | Salva raw HTML, marca para revisão manual |
| Referência ambígua (ex: "Lei 123" sem ano) | Log como AMBIGUOUS_REF, não enfileira |
| URL não encontrado no SUB-LINKS | Salva em tabela `missing_urls` para análise posterior |
| Race condition (arquivo criado por outro processo) | Re-verifica existência do arquivo antes de salvar |
| ChromaDB indexing falha após scraping OK | Marca como `completed_not_indexed`, worker reprocessa |
| Disco cheio | Verifica espaço (threshold: 1GB) antes de salvar, pausa se insuficiente |

### Garantias de Integridade

**Zero Duplicatas:**
- UNIQUE constraint em `scraping_queue.legal_reference`
- File system check antes de scraping
- Status "processing" previne múltiplos workers no mesmo job

**Retry Robusto:**
- Counter `attempts` na tabela
- Backoff exponencial previne thundering herd
- Após 3 falhas, marca failed e requer intervenção manual

## Configuração

### Variáveis de Ambiente

```bash
# .env
SCRAPING_WORKER_ENABLED=true
SCRAPING_WORKER_POLL_INTERVAL=5  # segundos
SCRAPING_WORKER_MAX_RETRIES=3
SCRAPING_WORKER_CONCURRENT_JOBS=1

QUEUE_BACKEND=sqlite  # ou 'redis' futuramente
QUEUE_DB_PATH=./data/scraping_queue.db
QUEUE_REDIS_URL=redis://localhost:6379

FIRECRAWL_TIMEOUT=60
FIRECRAWL_MAX_RETRIES=3

DOCS_PATH=./docs
MIN_DISK_SPACE_GB=1
```

### Inicialização

```python
# apps/backend/src/main.py
from agents.scraping_worker import ScrapingWorker
from agents.queue_manager import SQLiteQueueManager
import threading

def start_background_worker():
    if os.getenv("SCRAPING_WORKER_ENABLED") == "true":
        queue_manager = SQLiteQueueManager()
        worker = ScrapingWorker(queue_manager)
        thread = threading.Thread(target=worker.start, daemon=True)
        thread.start()
        logger.info("Scraping worker started")

@app.on_event("startup")
async def startup_event():
    start_background_worker()
```

## Nomenclatura de Arquivos

### Padrão Normalizado Técnico

| Referência Original | Arquivo Gerado |
|---------------------|----------------|
| Lei Complementar nº 227/2026 | `LC-227-2026.md` |
| Lei nº 14.133/2021 | `LEI-14133-2021.md` |
| Decreto 11.374/2023 | `DEC-11374-2023.md` |
| Medida Provisória 1.234/2024 | `MP-1234-2024.md` |
| Art. 156-A da Constituição Federal | `CF-art-156A.md` |
| Emenda Constitucional nº 132 | `EC-132.md` |

**Vantagens:**
- Consistente e previsível
- Fácil de gerar programaticamente
- Evita conflitos de nomenclatura
- Permite criar index JSON mapeando nomes técnicos → títulos descritivos

## Testes

### Unit Tests

```python
# tests/agents/test_citation_detector.py
def test_regex_extracts_lei_complementar():
    detector = CitationDetector()
    text = "Conforme LC 227/2026, art. 5º..."
    refs = detector._extract_from_text(text)
    assert "LC-227-2026" in refs

def test_normalize_handles_variations():
    detector = CitationDetector()
    variations = [
        "Lei Complementar nº 227/2026",
        "LC 227/2026",
        "LC 227, de 2026"
    ]
    for var in variations:
        assert detector._normalize([var])[0].normalized == "LC-227-2026"
```

### Integration Tests

```python
# tests/integration/test_scraping_pipeline.py
@pytest.mark.integration
def test_end_to_end_scraping(mock_firecrawl):
    # Setup
    queue = SQLiteQueueManager(":memory:")
    worker = ScrapingWorker(queue)

    # Enfileira job
    queue.enqueue(
        LegalReference("LC-227-2026"),
        "https://example.com/lc227",
        priority=1
    )

    # Worker processa
    job = queue.get_next_job()
    worker._process_job(job)

    # Assertions
    assert os.path.exists("/docs/LC-227-2026.md")
    assert queue.get_next_job() is None  # Fila vazia
```

### Checklist de Validação Manual

- [ ] Responder pergunta que cita lei não indexada
- [ ] Verificar job criado na fila SQLite (`SELECT * FROM scraping_queue`)
- [ ] Confirmar worker processa e salva arquivo em `/docs`
- [ ] Validar formato de nomenclatura do arquivo
- [ ] Verificar documento indexado no ChromaDB
- [ ] Fazer pergunta similar e confirmar usa documento novo

### Acceptance Criteria

- ✅ Detecta >90% das citações válidas (testar com amostra de 50 respostas)
- ✅ Zero duplicatas em `/docs` após 1000 operações
- ✅ Retry bem-sucedido em >80% dos casos de falha temporária
- ✅ Worker processa jobs em <60s (média, medida via histogram)
- ✅ Latência de resposta ao usuário permanece <30s

## Monitoring & Observability

### Métricas Prometheus

```python
# Counters
scraping_jobs_queued_total
scraping_jobs_completed_total
scraping_jobs_failed_total
documents_indexed_total

# Gauges
scraping_queue_size
scraping_worker_active

# Histograms
scraping_duration_seconds
indexing_duration_seconds
```

### Logs Estruturados

```python
logger.info("Job enqueued", extra={
    "legal_reference": ref.normalized,
    "priority": priority,
    "queue_size": queue.size()
})

logger.error("Scraping failed", extra={
    "legal_reference": ref.normalized,
    "url": job.source_url,
    "attempt": job.attempts,
    "error": str(e)
})
```

## Trade-offs e Decisões

### Decisões Arquiteturais

| Decisão | Escolha | Alternativas | Rationale |
|---------|---------|--------------|-----------|
| Timing | Pipeline separado + Cache/Fallback | Bloqueante, Streaming híbrido | Mantém latência <30s, enriquece progressivamente |
| Detecção | Híbrido (regex + metadata) | Só regex, Só LLM | Captura citações inline + fontes dos chunks |
| Fila | SQLite com abstração | Redis direto, JSON file | Zero-config, fácil migração futura |
| Nomenclatura | Normalizado técnico | Slug descritivo, Hash | Consistente, programático, previsível |
| Worker | Thread daemon | Processo separado, Celery | Simplicidade no MVP, escala depois |

### Trade-offs Aceitos

**Latência vs Completude:**
- ✅ Primeira pergunta sobre lei nova: resposta incompleta mas rápida
- ✅ Segunda pergunta sobre mesma lei: resposta completa (já scrapada)
- Alternativa rejeitada: Bloquear até scraping completar (violaria SLA de <30s)

**Scraping Seletivo:**
- ✅ Apenas leis citadas em respostas reais são scrapadas
- ✅ Leis raramente relevantes nunca consomem recursos
- Alternativa rejeitada: Scraping batch de todos os 917 links (desperdício)

**Storage Inicial Simples:**
- ✅ SQLite suficiente para <1000 jobs/dia
- ✅ Migração para Redis quando escalar (abstração já preparada)
- Alternativa rejeitada: Redis desde MVP (over-engineering)

## Próximos Passos

### Para Implementação

1. **Setup de infraestrutura:**
   - Criar git worktree isolado
   - Criar branch `feature/dynamic-corpus-expansion`

2. **Desenvolvimento (ordem sugerida):**
   - Implementar `LegalReferenceParser` (utils)
   - Implementar `CitationDetector` com testes
   - Criar schema SQLite + `QueueManager`
   - Implementar `ScrapingWorker` com retry logic
   - Integrar com RAG service (adicionar chunk tracking)
   - Configurar startup do worker no FastAPI

3. **Validação:**
   - Executar suite de testes
   - Validação manual com checklist
   - Monitorar métricas durante 24h de uso

### Evolução Futura

**Curto prazo (próximos 3 meses):**
- Dashboard admin para visualizar fila e status
- Endpoint API para triggering manual de scraping
- Alertas para falhas persistentes

**Médio prazo (6 meses):**
- Migração para Redis se volume justificar
- Worker separado em processo standalone
- Priorização inteligente baseada em analytics de uso

**Longo prazo (1 ano):**
- ML para prever quais leis serão consultadas (scraping preditivo)
- Versionamento de documentos legais (detectar alterações)
- Clustering de referências similares para deduplicação semântica

---

**Status:** Aprovado para implementação
**Próximo checkpoint:** Após conclusão do desenvolvimento, executar validação manual
