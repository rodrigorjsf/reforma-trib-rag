# ReformaTax — Product Requirements Document

**Version:** PRD v1.0  
**Status:** Ready for Development  
**Classification:** Confidential  
**Date:** January 2025  

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [User Persona](#2-user-persona)
3. [Core Features](#3-core-features)
4. [MVP Scope](#4-mvp-scope)
5. [User Journey](#5-user-journey)
6. [Technical Stack](#6-technical-stack)
7. [Security & Operational Reliability](#7-security--operational-reliability)
8. [Monetization Strategy](#8-monetization-strategy)

---

## 1. Executive Summary

| Metric | Value | Detail |
|--------|-------|--------|
| Target Market | ~5M | Accountants + SME owners in BR |
| MVP Timeline | 6 weeks | From zero to first deploy |
| Launch Cost | $0 | All free tiers |
| Revenue Target | $3K MRR | At 6 months |

### Problem Statement

The Brazilian Tax Reform (LC 214/2024) fundamentally restructures consumption taxation. Accountants and business owners need to understand its impact quickly and accurately, but the legal text is dense, cross-referenced, and constantly being supplemented by new regulations. There is no reliable, accessible tool that answers specific questions grounded exclusively in official sources — without hallucination or ambiguity.

### Core Value Proposition

ReformaTax is a **citation-grounded Q&A engine** that answers questions about the tax reform using only official legal sources (Planalto, DOU), always citing the specific article that supports each statement. It does not interpret — it locates, explains, and references. Users get clarity without legal risk.

### Success Criteria (MVP)

| Metric | Target | Description |
|--------|--------|-------------|
| Citation Rate | 100% | Every response cites source article |
| Hallucination Rate | < 2% | Responses unsupported by context |
| User Satisfaction | > 4/5 | Post-interaction rating |

---

## 2. User Persona

### Primary — Carlos, Contador (CPA)

| Attribute | Detail |
|-----------|--------|
| Age | 34 |
| Location | São Paulo |
| Role | Mid-career accountant at a regional firm |

**Profile:** Handles 40+ SME clients. Technically comfortable but not a developer. Uses Excel daily, Google for research.

**Daily Frustrations:**
- Spends 2–3h/week reading conflicting blog posts about the reform
- Can't quickly find which specific article applies to a client's situation
- Fears giving wrong advice due to misinterpretation
- New regulations drop weekly with no centralized view

**Behavior & Needs:**
- Needs answers in under 30 seconds
- Wants to see the legal source, not just an opinion
- Will pay for reliability — trust is the product
- Mobile usage during client meetings

---

### Secondary — Ana, Proprietária de MEI

| Attribute | Detail |
|-----------|--------|
| Age | 29 |
| Location | Belo Horizonte |
| Role | Small business owner (MEI → ME transition) |

**Profile:** No accounting background. Relies on her accountant but wants to understand her own situation independently.

**Daily Frustrations:**
- "Will this reform increase my taxes?"
- Can't parse legal language
- Overwhelmed by news contradictions

**Behavior & Needs:**
- Needs plain Portuguese explanations
- Low willingness to pay (freemium target)
- High shareability — word of mouth

---

## 3. Core Features

> Three features. Zero extras. Each one solves the primary pain point directly.

---

### 01 — Citation-Grounded Q&A

> **Why:** This is the product. Everything else is secondary.

**Pain Addressed:** Carlos spends hours searching for which article applies. He needs an answer in 10 seconds with the source visible.

**Specifications:**
- User submits a natural language question in Portuguese
- System retrieves relevant chunks from official legal corpus via hybrid search (vector + BM25)
- LLM generates response constrained to retrieved context only
- Every claim in the response includes inline citation: `[Art. X, §Y — LC 214/2024]`
- If no relevant context found, system responds with explicit "not found" — never fabricates
- Sources panel shows full text of cited articles for verification

**Out of Scope:** The system does NOT provide personalized tax calculations or legal advice for specific business situations.

---

### 02 — Live Source Freshness

> **Why:** The reform is actively being regulated. Stale data = wrong answers = lost trust.

**Pain Addressed:** New Instruções Normativas drop weekly. Carlos needs to know the system reflects the latest official text, not last month's.

**Specifications:**
- Automated weekly check against official PDF sources (Planalto, DOU)
- Content hash comparison detects updates without re-downloading unchanged docs
- Incremental re-indexing: only new/changed documents are re-processed
- UI badge shows "Sources updated: [date]" so users know data freshness
- Admin dashboard (internal) shows ingestion status and any parsing errors

**Out of Scope:** Real-time ingestion on publication. Weekly cadence is sufficient for this domain.

---

### 03 — Plain-Language Summary Mode

> **Why:** Secondary persona (Ana) can't parse legal text. This feature unlocks the freemium funnel.

**Pain Addressed:** Ana asks "How does this affect my MEI?" She needs a 3-sentence explanation, not a legal paragraph.

**Specifications:**
- Toggle on each response: "Modo Técnico" vs "Modo Simplificado"
- Simplified mode uses the same retrieved context but prompts the LLM to use plain language
- Citations are preserved in both modes (never sacrifice traceability for readability)
- Disclaimer shown in simplified mode: *"Esta explicação é simplificada. Consulte um profissional para decisões específicas."*

**Out of Scope:** Translation to other languages. Portuguese-only at MVP.

---

## 4. MVP Scope

### In Scope — MVP v1.0

- [x] Single Q&A interface with streaming responses
- [x] Citation inline + sources panel
- [x] Modo Técnico / Modo Simplificado toggle
- [x] Auth0 login (email + Google OAuth)
- [x] Free tier: 10 questions/day
- [x] Paid tier: unlimited questions
- [x] Disclaimer on every response
- [x] Sources freshness badge
- [x] Responsive design (desktop + mobile)
- [x] Conversation history (last 30 days)

### Post-MVP (v2.0+)

- [ ] Document upload (user's own docs)
- [ ] Multi-topic support beyond reforma
- [ ] Team/company plans with shared quotas
- [ ] PDF export of Q&A sessions
- [ ] Email digest of regulatory changes
- [ ] Integrations (API for third-party tools)
- [ ] Analytics dashboard for enterprise
- [ ] Multi-language support
- [ ] Custom branding / white-label
- [ ] Webhook notifications on source updates

### MVP Architecture Overview

```
User (Browser)
       │
       ▼
┌──────────────┐     ┌──────────────────┐
│  Next.js     │────▶│  FastAPI         │
│  (Vercel)    │     │  (Railway)       │
│  - Auth UI   │     │  - /query        │
│  - Chat UI   │     │  - /sources      │
│  - Citations │     │  - streaming SSE │
└──────────────┘     └────────┬─────────┘
                              │
                  ┌───────────┼───────────┐
                  ▼           ▼           ▼
           ┌────────┐  ┌──────────┐  ┌─────────┐
           │ChromaDB│  │  Ollama  │  │  Groq   │
           │(vetores│  │(embedding│  │  API    │
           │ local) │  │  local)  │  │(geração)│
           └────────┘  └──────────┘  └─────────┘
```

---

## 5. User Journey

> From discovery to first value — optimized for the shortest path to trust.

### Step 1 — Discovery
User finds ReformaTax via Google (SEO on reform keywords) or LinkedIn/Twitter mention.

*Mental model: "This might answer my question about CBS alíquotas."*

### Step 2 — Landing Page
Sees headline, one example Q&A with visible citation, trust signals (source badges). CTA: "Try free."

*Mental model: "It shows the actual law text. Seems reliable."*

### Step 3 — Sign Up
Auth0 modal — Google OAuth (one click) or email. No credit card. No long forms.

### Step 4 — First Question
Pre-filled suggestion chips: *"Como o CBS afeta MEI?"* / *"Quais são as alíquotas do IBS?"* User taps one or types own question.

### Step 5 — First Value ✓ `[KEY MOMENT]`
Response arrives with streaming text + citation panel opens automatically showing the source article. User clicks "Ver texto completo" and confirms accuracy.

> **This is the moment.** User sees: answer + source + can verify. Trust is built.

### Step 6 — Retention Hook
After 3rd question, soft paywall: *"Você usou 3 das 10 perguntas gratuitas hoje. Upgrade para ilimitado."* No block — just awareness.

---

### Onboarding Design Principles

| Principle | Rationale |
|-----------|-----------|
| Zero friction to first value | No tutorial, no onboarding wizard. User types a question within 15 seconds of landing. |
| Trust before monetization | The free tier must deliver genuine value. Paywall only appears after user has experienced quality. |
| Show, don't tell | Landing page shows a real Q&A example with real citations. No marketing copy about "AI-powered." |

---

## 6. Technical Stack

> Optimized for fast launch, low cost, and AI-agent-friendly code standards.

| Layer | Technology | Rationale | Cost |
|-------|-----------|-----------|------|
| Frontend | Next.js 14+ | SSR for SEO (critical for organic traffic on legal keywords). App Router + Server Components. TypeScript strict mode. | $0 — Vercel |
| Auth | Auth0 | Free tier: 25K MAU. MFA built-in. Google OAuth. SDK for Next.js is production-ready. | $0 — Free |
| Backend | FastAPI | Async native for SSE streaming. Strong typing (Pydantic). OpenAPI docs auto-generated — AI agents can consume the spec directly. | $0 — Railway |
| Vector DB | ChromaDB | Embedded in FastAPI process. Zero infra. Persists to Railway volume. Sufficient for < 500K vectors. | $0 |
| Embedding | Ollama + nomic-embed | Runs in Railway container. No API cost per query. nomic-embed: 768 dims, fast, good multilingual. | $0 |
| LLM | Groq (Mixtral) | Free tier: 14K TPM on Mixtral-8x7B. Sub-100ms latency. Best PT quality at this price point. Streaming native. | $0 — Free |
| Cache | Upstash Redis | Serverless. Free: 10K cmds/day. Caches repeated questions (high hit rate on common reform topics). | $0 — Free |
| Parsing | Marker (offline) | Runs locally during ingestion. Best open-source PDF→Markdown for tables. No API dependency. | $0 |
| Monitoring | Railway Logs + Sentry | Sentry free tier: 5K events/mo. Enough to catch hallucination spikes and errors in production. | $0 — Free |

### AI-Agent Compatibility

**OpenAPI-First Backend:** FastAPI auto-generates OpenAPI spec. Any AI agent (Claude, GPT, etc.) can discover and call endpoints without manual documentation.

**Strict TypeScript + Pydantic:** All contracts are typed. Pydantic models serve as source of truth for both validation and documentation. Zero ambiguity for code generation.

**Modular Service Boundaries:** Each service (parser, chunker, indexer, query engine) is isolated with clear interfaces. AI agents can modify one without breaking others.

---

## 7. Security & Operational Reliability

> Threat model, cost controls, and rate limiting for a solo-operated SaaS.

### Security Threat Model

| Priority | Threat | Mitigation |
|----------|--------|------------|
| 🔴 Critical | LLM Prompt Injection | All user input is sanitized before passing to LLM. System prompt and user prompt are separated. Context is injected server-side only — user never controls what enters the prompt. |
| 🔴 Critical | API Key Exposure | All API keys (Groq, Auth0) stored as environment variables on Railway. Never exposed to frontend. Frontend only calls your own FastAPI endpoints. |
| 🟠 High | Rate Limit Abuse / DDoS | Rate limiting at two layers: (1) Auth0 brute-force protection on login, (2) FastAPI middleware rate limit per user_id: 10 req/min free, 30 req/min paid. Redis-backed counters. |
| 🟠 High | Data Scraping / Bulk Export | Responses are generated per-question. No bulk export endpoint exists. Conversation history limited to 30 days and paginated. |
| 🟡 Medium | Unauthorized Access to Legal Corpus | Legal corpus is internal-only (ChromaDB on Railway). Not exposed via any API. Users only see LLM-generated responses + cited article excerpts. |
| 🔴 Critical | Hallucination in Production | Bounded prompt (system prompt enforces citation). Post-generation check: if response contains no citation markers, it is flagged and returned as "insufficient information." Sentry alerts on flagged responses. |

### Cost Management Strategy

**Cache-First Query:** Redis caches responses by question hash. Common questions (MEI, alíquotas, CBS vs IBS) have very high cache hit rate. Reduces Groq API calls by est. 60–70% at scale.

**Free Tier Quotas:** 10 questions/day for free users. Enforced via Redis counter per user_id per day (UTC). Prevents free-tier abuse. Quota resets at midnight UTC.

**LLM Token Budget:** `max_tokens` capped at 800 per response. Sufficient for cited answers. Prevents runaway generation costs. Monitor avg tokens/response via logs.

**Embedding Locally:** Zero cost per embedding. All embedding happens on Railway container via Ollama. No per-query API cost regardless of volume.

**Alert on Cost Spike:** Railway spend alerts at $10 and $25 thresholds. Groq usage dashboard monitored weekly. Any anomaly triggers immediate investigation.

**Graceful Degradation:** If Groq API is down or rate-limited, return cached response if available. If no cache, return "Service temporarily unavailable" — never silently fail.

### Rate Limit & Quota Matrix

| Resource | Free Tier | Paid Tier | Enforcement |
|----------|-----------|-----------|-------------|
| Questions / day | 10 | Unlimited | Redis counter, resets UTC midnight |
| Requests / minute | 5 | 30 | Redis sliding window per user_id |
| Response max tokens | 800 | 800 | LLM param, same for all tiers |
| Conversation history | 7 days | 30 days | DB TTL + scheduled cleanup |
| Concurrent sessions | 1 | 3 | Auth0 session management |

---

## 8. Monetization Strategy

> Realistic pricing for a niche B2B SaaS in the Brazilian legal-tech market.

### Pricing Tiers

#### Free — R$ 0/month
- 10 questions per day
- Citation-grounded responses
- Modo Simplificado + Técnico
- 7-day conversation history
- Community support (Discord)

#### Pro — R$ 49/month ⭐ Recommended
- Unlimited questions
- 30-day conversation history
- Priority response (lower latency)
- Email support
- Early access to new features
- PDF export of Q&A sessions
- *7-day free trial available*

#### Team — R$ 199/month
- Everything in Pro
- Up to 5 team members
- Shared conversation workspace
- Monthly usage report
- Dedicated Slack support
- Custom onboarding session

### Unit Economics — Per Paying User

| Metric | Value | Note |
|--------|-------|------|
| COGS (Pro) | ~$2 | Groq API + infra share |
| Gross Margin | ~96% | At R$ 49/mo (~$9 USD) |
| CAC Target | < $15 | Organic SEO + content |
| Payback Period | < 2 months | At target CAC |

### Revenue Projection — Conservative Scenario

| Month | Free Users | Pro Subs | Team Subs | MRR (R$) | Est. Infra Cost |
|-------|-----------|----------|-----------|----------|-----------------|
| 1–2 | 200 | 5 | 0 | 245 | ~$5 |
| 3–4 | 500 | 20 | 2 | 1,378 | ~$10 |
| 5–6 | 1,200 | 50 | 5 | 3,445 | ~$20 |
| 7–9 | 3,000 | 100 | 12 | 7,288 | ~$40 |
| 10–12 | 5,000 | 180 | 25 | 13,870 | ~$70 |

**Assumptions:** 2% free→paid conversion (industry avg for niche B2B tools). Growth driven primarily by SEO on long-tail reform keywords. Team tier requires manual outreach to accounting firms starting month 4.

### Acquisition Strategy (Zero Ad Spend)

| Channel | Priority | Strategy |
|---------|----------|----------|
| SEO Content | P0 | Blog posts answering specific reform questions. Target long-tail keywords: "reforma tributária MEI", "CBS alíquota serviços". Next.js SSR makes this viable from day 1. |
| LinkedIn Organic | P0 | Weekly posts about new regulations with the tool's answer as the content. Targets accountants and business owners directly. |
| Accountant Communities | P1 | Slack/WhatsApp groups for CPAs. Offer free access in exchange for feedback. Word-of-mouth in professional networks is the highest-converting channel in BR. |

---

*PRD v1.0 — ReformaTax MVP — January 2025*
