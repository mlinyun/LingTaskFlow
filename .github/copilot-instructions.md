# LingTaskFlow - GitHub Copilot Instructions

## Architecture Overview

LingTaskFlow (凌云智能任务管理平台) is a full-stack task management system designed for individual users:

- **Backend**: Django 5.2 REST API with JWT authentication, SQLite database
- **Frontend**: Vue 3 + Quasar Framework SPA with TypeScript and Vite
- **Environment**: Conda environment for backend, Node.js v22+ for frontend
- **API Documentation**: Auto-generated OpenAPI 3.0 docs via drf-spectacular

## Tech Stack & Dependencies

### Backend (`ling-task-flow-backend/`)

- **Framework**: Django 5.2.4 + Django REST Framework 3.16.0
- **Authentication**: JWT via `djangorestframework-simplejwt`
- **Database**: SQLite (dev), PostgreSQL-ready (production)
- **Features**: CORS support, filtering, pagination, caching, media uploads
- **Documentation**: DRF Spectacular for OpenAPI schema generation
- **Key Dependencies**: django-cors-headers, django-filter, Pillow, redis

### Frontend (`ling-task-flow-frontend/`)

- **Framework**: Vue 3.4+ + Quasar 2.16+ + TypeScript 5.5+
- **Build Tool**: Vite + @quasar/app-vite
- **State Management**: Pinia 3.0+ with Composition API
- **HTTP Client**: Axios 1.2+ with interceptors for JWT
- **Routing**: Vue Router 4+ with history mode
- **Styling**: SCSS + Material Icons + Roboto font

## Project Structure & Architecture

### Backend Structure

```
ling-task-flow-backend/
├── LingTaskFlow/              # Main Django app
│   ├── models.py             # User, Task models with UUID primary keys
│   ├── serializers.py        # DRF serializers with validation
│   ├── views.py              # ViewSets with permissions & filtering
│   ├── urls.py               # API routing patterns
│   ├── permissions.py        # Custom permission classes
│   ├── exceptions.py         # Custom exception handling
│   ├── filters.py            # Django-filter backends
│   └── utils.py              # Utilities and pagination classes
├── ling_task_flow_backend/
│   ├── settings.py           # Django configuration with DRF & JWT
│   └── urls.py               # Root URL patterns with API docs
└── templates/                # Django templates for admin/docs
```

### Frontend Structure

```
ling-task-flow-frontend/src/
├── boot/                     # App initialization plugins
│   ├── axios.ts             # API client with JWT interceptors
│   ├── auth.ts              # Authentication guards
│   └── i18n.ts              # Internationalization setup
├── components/               # Reusable Vue components
│   ├── dashboard/           # Dashboard-specific components
│   ├── layout/              # Layout components (header, drawer)
│   └── TaskCard.vue         # Core task display component
├── stores/                   # Pinia state management
│   └── auth.ts              # Authentication store with JWT handling
├── types/                    # TypeScript type definitions
├── layouts/MainLayout.vue    # Main app layout with drawer navigation
├── pages/                    # Route components (Login, Dashboard, etc.)
└── router/routes.ts          # Vue Router configuration
```

## Development Patterns & Conventions

### Backend API Patterns

- **Models**: Use UUID primary keys, soft delete patterns, timestamp tracking
- **Serializers**: Nested serialization for related models, custom validation
- **Views**: Class-based ViewSets with filtering, searching, ordering
- **Permissions**: Custom permissions inheriting from DRF base classes
- **URLs**: RESTful patterns with `/api/` prefix, versioning-ready
- **Authentication**: JWT with access/refresh token rotation

### Frontend Development Patterns

- **Components**: Composition API with `<script setup lang="ts">`
- **State**: Pinia stores with computed properties and async actions
- **API Calls**: Centralized via axios with automatic token management
- **Routing**: Protected routes with authentication guards
- **Styling**: Quasar components with custom SCSS variables
- **Types**: Strict TypeScript with comprehensive type definitions

### Configuration Details

- **Backend Port**: 8000 (Django dev server)
- **Frontend Port**: 9000 (Quasar dev server)
- **CORS**: Configured for localhost:9000 in Django settings
- **API Base URL**: `http://localhost:8000/api/`
- **Documentation**: Available at `http://127.0.0.1:8000/api/docs/`

## Environment & Dependencies

### Backend Environment

- **Python Environment**: Conda environment `ling-task-flow-backend`
- **Python Version**: 3.11+
- **Activation**: `conda activate ling-task-flow-backend`
- **Key Commands**:
  ```bash
  python manage.py runserver    # Start dev server
  python manage.py migrate      # Apply database migrations
  python manage.py createsuperuser  # Create admin user
  ```

### Frontend Environment

- **Node.js**: v22+ (multi-version support: v18, v20, v22)
- **Package Manager**: npm (preferred) or yarn
- **Key Commands**:
  ```bash
  npm run dev      # Start development server with HMR
  npm run build    # Production build
  npm run lint     # ESLint with Vue/TypeScript rules
  npm run format   # Prettier code formatting
  ```

## Integration & API Communication

### Authentication Flow

- JWT-based authentication with access/refresh tokens
- Token storage in LocalStorage via Quasar's LocalStorage API
- Automatic token refresh via axios interceptors
- Protected routes with navigation guards

### API Integration

- RESTful API design with consistent response format
- Standardized error handling with custom exception handler
- Request/response interceptors for token management
- TypeScript interfaces for API contracts

### Cross-Origin Configuration

- Frontend (Quasar): localhost:9000
- Backend (Django): localhost:8000
- CORS middleware configured for development environment
- Production-ready CORS settings available

## Development Workflow

1. **Environment Setup**: Activate conda environment for backend
2. **Database**: Migrations auto-applied, admin user creation as needed
3. **API Development**: Use DRF patterns with automatic documentation
4. **Frontend Development**: Component-driven with TypeScript strict mode
5. **Testing**: API testing via generated documentation interface
6. **Build**: Separate build processes for backend (collectstatic) and frontend (Quasar build)

This architecture supports rapid development while maintaining production readiness with proper separation of concerns,
comprehensive type safety, and automated API documentation.