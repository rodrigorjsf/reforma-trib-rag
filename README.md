# ReformaTax

AI-powered Q&A platform for Brazilian Tax Reform, built with React and FastAPI.

## Architecture Overview

This project follows a **simple dual-service architecture** with clear separation between frontend and backend:

```
├── apps/
│   ├── frontend/           # React + Vite application (TypeScript)
│   └── backend/            # FastAPI services (Python)
├── docs/                  # Documentation
└── dist/                  # Build output
```

## Services & Stack

### 🎨 Frontend (`apps/frontend`)
- **Technology**: React 19.2.0 + TypeScript + Vite
- **Styling**: Tailwind CSS v4.1.18
- **Build Tool**: Vite with rolldown-vite 7.2.5
- **Purpose**: User interface, chat UI, tax reform Q&A
- **Features**: Responsive design, dark theme, component-based architecture
- **Development**: Hot reload, ESLint, TypeScript strict mode

### 🔧 Backend (`apps/backend`) 
- **Technology**: FastAPI + Python
- **Data**: ChromaDB for vector storage
- **AI**: Groq API for LLM integration
- **Cache**: Redis for session management
- **Features**: Rate limiting, CORS, async processing, background workers
- **API**: RESTful endpoints with OpenAPI auto-documentation

## Getting Started

### Prerequisites
- Node.js 18+
- Python 3.8+
- npm 9+

### Setup

**Frontend:**
```bash
cd apps/frontend
# Note: This is a standalone app, not a monorepo workspace
# Remove workspace dependencies from package.json first, then:
npm install
npm run dev
# Frontend runs on http://localhost:3000
```

**Backend:**
```bash
cd apps/backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn src.main:app --reload
# Backend runs on http://localhost:8000
```

### Development

**Start Frontend:**
```bash
cd apps/frontend
npm run dev          # Development server with hot reload
npm run build        # Production build
npm run lint         # ESLint checking
npm run typecheck    # TypeScript type checking
npm run preview      # Preview production build
```

**Start Backend:**
```bash
cd apps/backend
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
# API docs available at http://localhost:8000/docs
```

### Quality Assurance

**Frontend:**
```bash
npm run lint         # ESLint
npm run typecheck    # TypeScript type checking
npx tsc --noEmit     # Additional type checking
```

**Backend:**
```bash
# API documentation: http://localhost:8000/docs
# Health check: http://localhost:8000/health
```

## API Endpoints

### Backend API (http://localhost:8000)

**Query Processing:**
- `POST /api/query` - Submit tax reform questions
- `GET /api/user/{user_id}` - Get user info and rate limits
- `GET /health` - Service health check

**Features:**
- Rate limiting (RPM and daily limits)
- User tiers (FREE/PRO)
- Citation-grounded responses
- Multi-modal prompt engineering

### Frontend Features

- **UI Components**: System prompts, chat interface, PRD viewer
- **Styling**: Dark theme, responsive design, Tailwind utilities
- **Type Safety**: Strict TypeScript, comprehensive interfaces
- **Development**: Hot reload, linting, type checking

## Technical Stack

**Frontend:**
- React 19.2.0 with TypeScript 5.9
- Vite (rolldown-vite 7.2.5) for fast development
- Tailwind CSS v4.1.18 for styling
- ESLint + TypeScript ESLint for code quality

**Backend:**
- FastAPI with Python
- ChromaDB for vector storage and RAG
- Groq API for AI/LLM integration
- Redis for caching and session management
- Pydantic v2 for data validation

**Development Tools:**
- Vite for frontend bundling
- Uvicorn for backend serving
- ESLint for linting
- TypeScript strict mode for type safety

## Current Implementation Status

✅ **Completed:**
- Frontend React application with Tailwind styling
- Backend FastAPI with rate limiting and CORS
- Basic API structure with health checks
- Mock query responses with citations
- Background worker system for content processing

🚧 **In Progress:**
- RAG pipeline implementation
- ChromaDB vector integration
- Actual LLM calls to Groq API
- Content scraping and processing

📋 **Next Steps:**
1. Complete RAG pipeline with ChromaDB
2. Implement Groq API integration
3. Add authentication system
4. Deploy to production infrastructure
5. Add comprehensive testing

This architecture provides a solid foundation for building AI-powered tax reform Q&A services while maintaining clean separation between presentation and business logic.