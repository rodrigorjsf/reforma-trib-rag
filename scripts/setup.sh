#!/bin/bash

# ReformaTax Monorepo Setup Script

echo "🚀 Setting up ReformaTax monorepo..."

# Install dependencies for all packages
echo "📦 Installing dependencies..."
npm install

# Build all packages in order
echo "🔨 Building packages..."
npm run build --workspace=@reform-tax/types
npm run build --workspace=@reform-tax/shared  
npm run build --workspace=@reform-tax/utils

# Build frontend
echo "🎨 Building frontend..."
npm run build --workspace=@reform-tax/frontend

echo "✅ Monorepo setup complete!"
echo ""
echo "📁 Project Structure:"
echo "├── apps/"
echo "│   ├── frontend/     - React/Next.js application"
echo "│   └── backend/      - FastAPI Python services"  
echo "├── packages/"
echo "│   ├── types/        - Shared TypeScript definitions"
echo "│   ├── shared/       - Common business logic"
echo "│   └── utils/        - Utility functions"
echo "└── docs/           - Documentation"
echo ""
echo "🎯 Available commands:"
echo "  npm run dev              - Start all services"
echo "  npm run dev:frontend     - Start frontend only"
echo "  npm run dev:backend      - Start backend only"
echo "  npm run build            - Build all packages"
echo "  npm run lint             - Lint all packages"
echo "  npm run typecheck        - Type check all packages"