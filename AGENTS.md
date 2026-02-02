# AGENTS.md - Development Guidelines for ReformTax

This document contains coding standards, conventions, and commands for agentic coding agents working in this repository.

## Project Overview

**ReformaTax** is a React + TypeScript application for Brazilian tax reform documentation and analysis. The project focuses on providing accurate legal information with proper citation handling and multi-modal prompt engineering.

## Build, Lint & Test Commands

```bash
# Development server with hot reload
npm run dev

# Production build
npm run build

# Linting and type checking (run after changes)
npm run lint

# Preview production build locally
npm run preview

# Type checking (manual, since build includes it)
npx tsc --noEmit
```

**Important**: Always run `npm run lint` and `npx tsc --noEmit` after making changes to ensure code quality.

## Code Style Guidelines

### TypeScript & JavaScript
- **Type Safety**: Always use TypeScript. All components must have proper interfaces and types.
- **Strict Mode**: Project uses strict TypeScript (`"strict": true`). No implicit `any`.
- **Imports**: Use ES6 import syntax. Group imports: external libraries first, then internal modules.
- **Interfaces**: Define interfaces for all component props and data structures. Use `type` for unions/intersections.
- **Enums**: Use TypeScript enums for fixed sets of values (e.g., `Veredicto`, `Severidade`).

### React Components
- **Functional Components**: Only use functional components with hooks.
- **Props Interface**: Always define props interface with TypeScript.
- **Children**: Use `ReactNode` type for children props.
- **Default Props**: Use default parameter values instead of `defaultProps`.
- **State Management**: Use `useState` for local state. Context hooks for shared state.

### File Naming & Structure
- **Component Files**: PascalCase (`SystemPrompts.tsx`, `PRDReformaTributariaSaaS.tsx`)
- **Utility Files**: camelCase (`utils/formatters.ts`)
- **Types/Interfaces**: Use `types/` directory for shared interfaces
- **Constants**: Use camelCase for constants (`promptData`, `colorMap`)

### CSS & Styling
- **Tailwind CSS**: All styling uses Tailwind utility classes. No custom CSS except for base imports.
- **Responsive Design**: Mobile-first approach with responsive prefixes (`md:`, `lg:`)
- **Color Scheme**: Consistent use of slate colors for backgrounds with accent colors (emerald, violet, amber, sky, rose)
- **Dark Theme**: All components designed for dark theme (`bg-slate-950`, `text-slate-100`)

### Import Patterns

```typescript
// External libraries first
import React, { useState, type ReactNode } from "react"

// Internal modules
import Component from "./Component"
import type { ComponentProps } from "./types"

// Styling (minimal, just Tailwind import)
import "./index.css"
```

### Error Handling
- **Type Safety**: Use TypeScript's strict mode to catch errors at compile time
- **Props Validation**: Use interfaces for all component props
- **Optional Chaining**: Use optional chaining (`?.`) for nested object access
- **Fallback Values**: Provide sensible defaults for optional data

### Performance Guidelines
- **React.memo**: Use for components that re-render with same props
- **useCallback/useMemo**: For expensive computations and stable function references
- **Code Splitting**: Lazy load large components with `React.lazy()`
- **Bundle Size**: Monitor bundle size in build output

## Configuration Files

### ESLint Configuration
- Uses flat config format (`eslint.config.js`)
- TypeScript ESLint rules enabled
- React hooks and refresh plugins configured
- Global ignores for `dist` directory

### TypeScript Configuration
- Multi-project setup with `tsconfig.json` references
- Strict mode enabled with `noUnusedLocals` and `noUnusedParameters`
- ESNext target with DOM types
- Vite client types included

### Tailwind Configuration
- Standard Tailwind v4 setup with PostCSS
- Content paths configured for src directory
- Custom theme extensions in `tailwind.config.js`

## Component Patterns

### Button Components
```typescript
interface ButtonProps {
  children: ReactNode
  variant?: "primary" | "secondary"
  onClick?: () => void
  disabled?: boolean
  className?: string
}

const Button = ({ children, variant = "primary", onClick, disabled = false, className = "" }: ButtonProps) => {
  const baseClasses = "px-4 py-2 rounded border font-mono text-xs transition-colors"
  const variantClasses = variant === "primary" 
    ? "bg-emerald-900/40 text-emerald-300 border-emerald-700/50"
    : "bg-slate-800/60 text-slate-300 border-slate-600/50"
  
  return (
    <button
      className={`${baseClasses} ${variantClasses} ${className}`}
      onClick={onClick}
      disabled={disabled}
    >
      {children}
    </button>
  )
}
```

### Badge Pattern
```typescript
interface BadgeProps {
  children: ReactNode
  color?: "emerald" | "violet" | "amber" | "sky" | "rose" | "slate"
  className?: string
}

const Badge = ({ children, color = "emerald", className = "" }: BadgeProps) => {
  const colors: Record<string, string> = {
    emerald: "bg-emerald-900/40 text-emerald-300 border-emerald-700/50",
    // ... other colors
  }
  
  return (
    <span className={`inline-block text-xs font-mono px-2 py-0.5 rounded border ${colors[color]} ${className}`}>
      {children}
    </span>
  )
}
```

## Testing Approach

**Note**: This project currently doesn't have tests configured. When adding tests:
1. Use Vitest (Vite's preferred testing framework)
2. Follow React Testing Library patterns
3. Test component behavior, not implementation
4. Mock external dependencies in `__mocks__/`

## Security Considerations

- **No Direct DOM Manipulation**: Use React refs only when necessary
- **XSS Prevention**: Use React's built-in XSS protection for dynamic content
- **CSP Headers**: Consider Content Security Policy for production
- **Environment Variables**: Use `.env` files for secrets (never commit)

## Git Workflow

1. Create feature branches from main
2. Make atomic, focused commits
3. Run `npm run lint` before committing
4. Ensure build passes: `npm run build`
5. Use conventional commit messages when possible

## Common Patterns to Avoid

- ❌ Inline styles (use Tailwind classes)
- ❌ `any` types (use proper TypeScript interfaces)
- ❌ Direct state mutations (use immutable updates)
- ❌ Prop drilling for simple cases (use React Context)
- ❌ Large, monolithic components (break down into smaller ones)

## Development Tips

- **Hot Reload**: Development server supports HMR
- **Type Checking**: Use editor TypeScript integration for real-time feedback
- **Tailwind IntelliSense**: Configure for better class suggestions
- **Bundle Analysis**: Use `npm run build -- --analyze` for bundle insights

## Package Management

- **Node Version**: Use Node.js 18+ (check `.nvmrc` if present)
- **Dependencies**: Prefer exact versions in package.json
- **Security Updates**: Regularly audit with `npm audit`
- **Lock File**: Commit `package-lock.json` for reproducible builds

## When Working on This Codebase

1. Always check existing components for patterns before creating new ones
2. Follow the established color scheme and design system
3. Maintain consistency with existing file naming and structure
4. Test across different screen sizes (responsive design)
5. Ensure proper TypeScript types for all new code
6. Run linting and build before creating PRs

This codebase prioritizes type safety, consistency, and maintainability. Follow these guidelines to ensure high-quality contributions.