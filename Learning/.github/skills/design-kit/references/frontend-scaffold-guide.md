# Frontend Scaffold Guide

## SPA Structure Principles

### Pages vs Components
- **Page** (`/pages/`): corresponds to a route, owns data fetching
- **Component** (`/components/`): reusable UI piece, receives props only
- **Feature** (`/features/`): self-contained domain slice (state + components + API)

### Folder Structure Convention (Feature-Sliced Design)

```
src/
├── pages/                 # Route-level pages (thin — delegate to features)
│   └── <PageName>/
│       ├── index.tsx
│       └── <PageName>.test.tsx
├── features/              # Self-contained feature slices
│   └── <feature-name>/
│       ├── index.ts       # Public API
│       ├── components/
│       ├── hooks/
│       ├── store.ts
│       └── api.ts
├── entities/              # Domain types shared across features
│   └── <entity>/
│       ├── types.ts
│       └── api.ts
├── shared/                # Pure utilities, no domain logic
│   ├── ui/                # Generic components (Button, Modal, etc.)
│   ├── api/               # API client setup (axios instance)
│   ├── hooks/             # Generic hooks
│   └── utils/
├── app/                   # App config (routes, providers, store)
│   ├── routes.tsx
│   ├── providers.tsx
│   └── store.ts
└── styles/
```

## Microfrontend (MFE) Architecture

### Module Federation Setup (Webpack 5 / Vite)

```
shell-app/                  # Host application
├── module-federation.config.ts
│   remotes: {
│     productApp: 'product@http://localhost:3001/remoteEntry.js',
│     orderApp: 'order@http://localhost:3002/remoteEntry.js',
│   }

product-app/                # Remote MFE
├── module-federation.config.ts
│   exposes: {
│     './ProductList': './src/features/product/ProductList',
│     './ProductDetail': './src/features/product/ProductDetail',
│   }
```

### MFE Communication Patterns
| Pattern | When |
|---------|------|
| Custom events (`window.dispatchEvent`) | Cross-MFE loose events |
| Shared state via shell's store | Tight shared state |
| URL/route params | Navigation context |
| Shared auth context | JWT token passing |

## Angular-Specific Patterns

### Lazy-Loaded Feature Modules
```
app/
├── core/                  # Singleton services (guards, interceptors, auth)
├── shared/                # Shared module (common components/pipes/directives)
└── features/
    └── <feature>/
        ├── <feature>.module.ts         # Lazy loaded
        ├── <feature>-routing.module.ts
        ├── components/
        ├── services/
        ├── models/
        └── store/                     # NgRx or Akita (if used)
```

### MFE in Angular — Native Federation
Use `@angular-architects/native-federation` for Angular MFEs.

## State Management Guidelines

| Framework | Library | When |
|-----------|---------|------|
| React | Zustand | Simple global state |
| React | Tanstack Query | Server state, caching |
| React | Redux Toolkit | Complex domain state |
| Angular | NgRx + effects | Large apps, complex state |
| Angular | Signals (Angular 17+) | Simple reactive state |
| Vue | Pinia | Any Vue app |

## Routing Convention

```
/                          # Home / Dashboard
/<resource>                # List page (US-NNN: View <Resource> List)
/<resource>/new            # Create form
/<resource>/:id            # Detail view
/<resource>/:id/edit       # Edit form
```

## Environment Configuration

All API base URLs and feature flags via env files:
- `.env.development` — local dev
- `.env.staging` — staging env
- `.env.production` — production
