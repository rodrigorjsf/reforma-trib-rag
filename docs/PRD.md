# ReformaTax - AI-powered Q&A Platform for Brazilian Tax Reform

## Problem Statement

The Brazilian Tax Reform (LC 214/2024) fundamentally restructures consumption taxation, creating immediate uncertainty for 5M+ accountants and business owners. These professionals spend 2-3 hours weekly searching through dense, cross-referenced legal texts to answer client questions, with no reliable tool that provides citation-grounded answers without hallucination risk.

## Evidence

- **Market Size**: ~5M accountants + SME owners in Brazil need immediate clarity on tax reform changes
- **Time Cost**: Accountants spend 2-3h/week reading conflicting blog posts and legal sources
- **Risk Factor**: Wrong tax advice can lead to legal penalties - professionals need verifiable sources
- **Regulatory Velocity**: New regulations drop weekly with no centralized tracking system
- **Current Gap**: No existing tool provides citation-grounded Q&A exclusively from official sources

## Proposed Solution

ReformaTax is a citation-grounded Q&A engine that answers questions about tax reform using only official legal sources (Planalto, DOU), always citing specific articles that support each statement. The platform combines RAG retrieval with strict prompt engineering to ensure every response includes inline citations and verifiable source references, eliminating hallucination risk while delivering answers in under 30 seconds.

## Key Hypothesis

We believe citation-grounded Q&A with official legal sources will reduce research time by 80% for accountants while providing trustworthy answers for business owners. We'll know we're right when we achieve <2% hallucination rate with 100% citation compliance and >4/5 user satisfaction.

## What We're NOT Building

- **Personalized tax calculations** - We provide information, not specific tax advice for individual situations
- **Legal interpretation services** - We locate and explain legal text, don't provide professional legal opinions
- **Multi-topic expansion** - Focusing exclusively on tax reform (not broader legal or accounting domains)
- **Real-time regulatory monitoring** - Weekly updates are sufficient for this domain's pace

## Success Metrics

| Metric | Target | How Measured |
|--------|--------|--------------|
| Citation Rate | 100% | Automated check that every response includes source citations |
| Hallucination Rate | <2% | Manual audit of responses against source documents |
| User Satisfaction | >4/5 | Post-interaction rating system |
| Time to Answer | <30 seconds | Backend performance monitoring |
| Free-to-Paid Conversion | 2% | User progression through pricing tiers |

## Open Questions

- [ ] Will users trust AI-generated legal information even with citations?
- [ ] What is the optimal balance between technical vs simplified language modes?
- [ ] How frequently do new regulations actually require system updates?
- [ ] What price point maximizes conversion while maintaining accessibility?

---

## Users & Context

**Primary User: Carlos - Contador (CPA)**
- **Who**: 34-year-old accountant at regional firm, handles 40+ SME clients
- **Current behavior**: Uses Google search, reads conflicting blog posts, spends 2-3h/week on reform research
- **Trigger**: Client asks specific question about reform impact on their business situation
- **Success state**: Gets accurate answer with legal citation in under 30 seconds during client meeting

**Secondary User: Ana - MEI Business Owner**
- **Who**: 29-year-old small business owner transitioning from MEI to ME
- **Current behavior**: Overwhelmed by contradictory news, can't parse legal language
- **Trigger**: Wants to understand how reform affects her business taxes
- **Success state**: Gets plain-language explanation she can understand and act on

**Job to Be Done**
When I have a client question about tax reform, I want to quickly find the exact legal article that applies, so I can provide accurate advice with verifiable sources.

**Non-Users**
Large enterprises with in-house legal teams, international businesses, users seeking personalized tax advice or legal consultation services.

---

## Solution Detail

### Core Capabilities (MoSCoW)

| Priority | Capability | Rationale |
|----------|------------|-----------|
| Must | Citation-Grounded Q&A | Core product - every answer must cite specific legal articles |
| Must | Live Source Freshness | Reform is actively regulated - stale data creates wrong answers |
| Must | Dual Language Modes | Technical for accountants, simplified for business owners |
| Should | Conversation History | Users need reference to previous queries |
| Should | Mobile Responsive | Accountants need access during client meetings |
| Could | PDF Export | Nice for documentation but not core to value proposition |
| Won't | Multi-language Support | Portuguese-only at MVP, market is Brazilian |

### MVP Scope

Single Q&A interface with streaming responses, inline citations, source panel, technical/simplified mode toggle, Auth0 authentication, 10 free questions daily with unlimited paid tier, and responsive design.

### User Flow

1. User discovers via SEO or social mention
2. Lands on page showing real Q&A example with citations
3. Signs up via Google OAuth (no credit card)
4. Asks first question (suggested chips or custom)
5. Receives streaming response with citations + source panel
6. Sees value and converts to paid tier after 3 questions

---

## Technical Approach

**Feasibility**: HIGH

**Architecture Notes**
- Next.js 14+ with SSR for SEO on legal keywords
- FastAPI backend with streaming SSE responses
- ChromaDB for vector storage embedded in process
- Groq API for LLM generation (Mixtral-8x7B)
- Ollama local embedding for zero per-query cost
- Auth0 for authentication with free tier limits

**Technical Risks**

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| LLM Hallucination | Medium | Strict prompt engineering + citation enforcement + validator LLM |
| Groq Rate Limits | Low | Response caching with Redis + fallback to cached responses |
| PDF Parsing Errors | Medium | Marker offline parser + manual review pipeline |
| Vector Search Quality | Medium | Hybrid search (vector + BM25) + relevance threshold tuning |

---

## Implementation Phases

| # | Phase | Description | Status | Parallel | Depends | PRP Plan |
|---|-------|-------------|--------|----------|---------|----------|
| 1 | Infrastructure Setup | Deploy Next.js + FastAPI + Auth0 + DB | pending | - | - | - |
| 2 | Legal Corpus Ingestion | Build PDF parsing + chunking + indexing pipeline | pending | - | 1 | - |
| 3 | Q&A Core Engine | RAG retrieval + LLM generation + citation formatting | pending | with 4 | 1, 2 | - |
| 4 | Frontend Interface | Chat UI + source panel + mode toggle + responsive design | pending | with 3 | 1 | - |
| 5 | Auth & Limits | User authentication + rate limiting + quota enforcement | pending | - | 1 | - |
| 6 | Testing & Launch | Integration testing + hallucination detection + production deploy | pending | - | 3, 4, 5 | - |

### Phase Details

**Phase 1: Infrastructure Setup**
- **Goal**: Deployable foundation with all services connected
- **Scope**: Next.js on Vercel, FastAPI on Railway, Auth0 configuration, Redis setup
- **Success signal**: Services respond to health checks with proper CORS configuration

**Phase 2: Legal Corpus Ingestion**
- **Goal**: Automated pipeline for processing official legal documents
- **Scope**: PDF download from Planalto/DOU, Markdown conversion with Marker, chunking strategy, ChromaDB indexing
- **Success signal**: Can query and retrieve relevant legal chunks for sample questions

**Phase 3: Q&A Core Engine**
- **Goal**: Working RAG system with citation-grounded responses
- **Scope**: Vector search implementation, Groq API integration, prompt engineering for citations, response streaming
- **Success signal**: Sample questions return accurate responses with proper citation formatting

**Phase 4: Frontend Interface**
- **Goal**: Complete user interface for Q&A interaction
- **Scope**: Chat interface, streaming response display, source panel, technical/simplified toggle, mobile responsive design
- **Success signal**: Users can complete full Q&A flow from question to cited answer

**Phase 5: Auth & Limits**
- **Goal**: User management and usage control
- **Scope**: Auth0 integration, user session management, rate limiting, quota tracking, upgrade prompts
- **Success signal**: Free users limited to 10 questions/day, paid users have unlimited access

**Phase 6: Testing & Launch**
- **Goal**: Production-ready system with quality assurance
- **Scope**: Integration testing, hallucination rate measurement, performance optimization, production deployment
- **Success signal**: System passes quality thresholds and handles real user traffic

### Parallelism Notes

Phases 3 and 4 can run in parallel as backend API and frontend can be developed against mock endpoints. Phase 5 depends on Phase 1 completion but can be developed in parallel with Phase 3 and 4 once auth is configured.

---

## Decisions Log

| Decision | Choice | Alternatives | Rationale |
|----------|--------|--------------|-----------|
| Frontend Framework | Next.js 14+ | Create React App, Remix | SSR critical for SEO on legal keywords |
| Vector Database | ChromaDB | Pinecone, Weaviate | Zero infra cost, embedded in process |
| LLM Provider | Groq (Mixtral) | OpenAI, Anthropic | Free tier with sub-100ms latency |
| Embedding | Ollama + nomic-embed | OpenAI text-embedding | Zero per-query cost, runs locally |
| Authentication | Auth0 | Firebase Auth, Custom | Free tier covers 25K MAU, battle-tested |

---

## Research Summary

**Market Context**
Brazilian tax reform creates immediate need for reliable legal information. Existing solutions include law firm blogs, government portals, and generic AI assistants. None provide citation-grounded Q&A with verified sources. Professional accountants willing to pay for reliability due to legal risk exposure.

**Technical Context**
RAG architecture well-established for legal domain. Hybrid search (vector + keyword) improves recall. Citation enforcement through prompt engineering reduces hallucination risk. Local embedding eliminates per-query costs while maintaining quality.

---

*Generated: 2025-01-31*
*Status: DRAFT - needs validation*