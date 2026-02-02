# AGENTS.md - Development Guidelines for ReformTax

This document contains coding standards, conventions, and commands for agentic coding agents working in this repository.

## Project Overview

**ReformaTax** is a React + TypeScript (frontend) + Python (backend) application for Brazilian tax reform documentation and analysis. The project focuses on providing accurate legal information with proper citation handling and multi-modal prompt engineering.

## Structure-Specific Guidelines

This repository has separate development guidelines for each application component:

### Frontend (React + TypeScript)
📁 **Location**: `apps/frontend/AGENTS.md`
- **Framework**: React with TypeScript
- **Styling**: Tailwind CSS
- **Standards**: [React Rules of Hooks](https://react.dev/reference/rules) and Component Purity
- **Key Features**: Component purity, functional components, strict TypeScript

### Backend (Python + FastAPI)
📁 **Location**: `apps/backend/AGENTS.md`
- **Framework**: FastAPI with Python 3.11+
- **Standards**: [PEP 8 – Style Guide for Python Code](https://peps.python.org/pep-0008/)
- **Key Features**: Type hints, Pydantic models, ruff linting/formatting

## Quick Reference

### Frontend Commands
```bash
cd apps/frontend
npm run dev          # Development server
npm run build        # Production build
npm run lint         # ESLint + TypeScript check
npm run preview      # Preview production build
```

### Backend Commands
```bash
cd apps/backend
uvicorn src.main:app --reload    # Development server
pytest                           # Run tests
ruff check src/                   # Linting
ruff format src/                  # Code formatting
```

## Development Workflow

1. **Navigate to the appropriate app directory** before starting work
2. **Follow the specific coding standards** for that application
3. **Run the appropriate linting and test commands** for the app you're working on
4. **Commit changes** with conventional commit messages when possible

## Cross-Cutting Concerns

Both applications share these principles:
- **Type Safety**: Strong typing with TypeScript and Python type hints
- **Testing**: Comprehensive test coverage
- **Documentation**: Clear documentation for public APIs
- **Security**: Input validation and secure coding practices
- **Code Quality**: Strict linting and formatting standards

## Getting Started

When working on this codebase:
1. First determine whether you're working on **frontend** or **backend**
2. Navigate to the appropriate directory: `cd apps/frontend/` or `cd apps/backend/`
3. Read the specific `AGENTS.md` file in that directory for detailed guidelines
4. Follow the workflow and standards specific to that application

This modular approach ensures that each application follows best practices for its respective technology stack while maintaining overall project consistency.