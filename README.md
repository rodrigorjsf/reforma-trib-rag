# ReformaTax Monorepo

AI-powered Q&A platform for Brazilian Tax Reform, organized as a modular monorepo with clear service boundaries.

## Architecture Overview

This monorepo follows the **Modular Service Boundaries** principle from the Technical Stack specification, enabling AI agents to modify one service without breaking others:

```
├── apps/                    # Applications
│   ├── frontend/            # React/Next.js application (TypeScript)
│   └── backend/             # FastAPI services (Python)
├── packages/               # Shared libraries
│   ├── types/             # TypeScript definitions
│   ├── shared/            # Common business logic
│   └── utils/            # Utility functions
├── docs/                  # Documentation
└── scripts/               # Build and development scripts
```

## Services & Boundaries

### 🎨 Frontend (`apps/frontend`)
- **Technology**: Next.js 14+ with TypeScript
- **Purpose**: User interface, chat UI, auth integration
- **Boundary**: Pure presentation layer, no business logic
- **Dependencies**: `@reform-tax/types`, `@reform-tax/shared`

### 🔧 Backend (`apps/backend`) 
- **Technology**: FastAPI with TypeScript
- **Purpose**: Query processing, RAG pipeline, API endpoints
- **Boundary**: Core business logic and data processing
- **Dependencies**: `@reform-tax/types`, `@reform-tax/shared`, `@reform-tax/utils`

### 📋 Types (`packages/types`)
- **Technology**: TypeScript definitions only
- **Purpose**: Shared interfaces and type definitions
- **Boundary**: Pure type definitions, no runtime code
- **Consumed by**: All packages

### 🔄 Shared (`packages/shared`)
- **Technology**: TypeScript utility functions
- **Purpose**: Common business logic (validation, formatting)
- **Boundary**: Stateless pure functions
- **Dependencies**: `@reform-tax/types`

### 🛠️ Utils (`packages/utils`)
- **Technology**: TypeScript helper functions
- **Purpose**: Backend utilities (rate limiting, retry, etc.)
- **Boundary**: Infrastructure-agnostic utilities
- **Dependencies**: `@reform-tax/types`, `@reform-tax/shared`

## Getting Started

### Prerequisites
- Node.js 18+
- npm 9+

### Setup
```bash
# Clone and setup
git clone <repository>
cd reform-tax
chmod +x scripts/setup.sh
./scripts/setup.sh
```

### Development
```bash
# Start all services
npm run dev

# Start individual services
npm run dev:frontend    # Frontend on http://localhost:3000
npm run dev:backend     # Backend on http://localhost:3001
```

### Building
```bash
# Build all packages
npm run build

# Build specific package
npm run build --workspace=@reform-tax/frontend
npm run build --workspace=@reform-tax/backend
```

### Quality Assurance
```bash
# Lint all packages
npm run lint

# Type checking
npm run typecheck

# Clean build artifacts
npm run clean
```

## AI Agent Compatibility

This monorepo is designed for AI agent development:

### 🔄 Modular Service Boundaries
Each service has:
- Clear interfaces and contracts
- Minimal coupling
- Independent deployment capability

### 📋 OpenAPI-First Backend
FastAPI auto-generates OpenAPI specifications for endpoint discovery.

### 🎯 Strict TypeScript
All contracts are typed with Pydantic-style validation patterns.

### 📦 Workspace Management
npm workspaces enable:
- Cross-package type checking
- Atomic dependency management  
- Consistent build processes

## Development Workflow

1. **Feature Development**: Work within service boundaries
2. **Interface Changes**: Update `packages/types` first
3. **Cross-Service Updates**: Build packages in dependency order
4. **Testing**: Run type checking across all packages
5. **Deployment**: Services deploy independently

## Technical Stack

- **Frontend**: Next.js 14+, React 19, TypeScript, Tailwind CSS
- **Backend**: FastAPI, TypeScript, ChromaDB, Groq API
- **Infrastructure**: Vercel (frontend), Railway (backend)
- **Development**: Vite, npm workspaces, ESLint

## Next Steps

1. Implement RAG pipeline in backend
2. Add ChromaDB integration
3. Connect frontend to backend APIs
4. Implement authentication flow
5. Add rate limiting and quotas

This structure enables rapid, independent development while maintaining clear boundaries for AI agent assistance.