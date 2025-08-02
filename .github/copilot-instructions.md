# LingTaskFlow - GitHub Copilot Instructions

## Architecture Overview

LingTaskFlow is a full-stack task management system with:

- **Backend**: Django 5.2 REST API (`ling-task-flow-backend/`) running in Conda environment
- **Frontend**: Vue 3 + Quasar Framework SPA (`ling-task-flow-frontend/`) using Node.js v22
- **Database**: SQLite (development), designed for individual users
- **Environment**: Anaconda Python environment for backend isolation

## Project Structure & Key Files

### Backend (`ling-task-flow-backend/`)

- **Main app**: `LingTaskFlow/` - Core task management logic
- **Settings**: `ling_task_flow_backend/settings.py` - Django configuration
- **Entry point**: `manage.py` - Standard Django management commands
- **Templates**: `templates/` - Django template directory (likely for admin/docs)

### Frontend (`ling-task-flow-frontend/`)

- **Framework**: Quasar 2.x + Vue 3 + TypeScript + Vite
- **Layout**: `src/layouts/MainLayout.vue` - Standard drawer + toolbar layout
- **Routing**: Hash-based routing (`quasar.config.ts` line 44)
- **State**: Pinia stores in `src/stores/`
- **Styling**: SCSS with Quasar variables

## Development Workflows

### Backend Development (Conda Environment)

```bash
# Activate conda environment
conda activate ling-task-flow-backend

# Navigate to backend directory
cd ling-task-flow-backend

# Django management commands
python manage.py runserver          # Start Django dev server
python manage.py makemigrations     # Create DB migrations
python manage.py migrate            # Apply migrations
python manage.py createsuperuser    # Create admin user
```

### Frontend Development (Node.js v22)

```bash
cd ling-task-flow-frontend
npm install                         # Install dependencies
npm run dev                         # Start Quasar dev server with HMR
npm run build                       # Production build
npm run lint                        # ESLint with Vue/TypeScript support
npm run format                      # Prettier formatting
```

## Project-Specific Conventions

### Django App Structure

- Main Django app is named `LingTaskFlow` (capitalized)
- App config: `'LingTaskFlow.apps.LingtaskflowConfig'` in INSTALLED_APPS
- Templates directory at project root level (not app level)

### Frontend Patterns

- **Boot files**: `src/boot/` for global plugins (axios, i18n)
- **Components**: Use Composition API with `<script setup lang="ts">`
- **Routing**: Lazy-loaded components with `() => import()`
- **Store**: Pinia with HMR support pattern in stores
- **Styling**: Material Icons + Roboto font from Quasar extras

### TypeScript Configuration

- Strict TypeScript enabled (`quasar.config.ts`)
- Vue shims enabled for `.vue` file support
- Target: ES2022, Node 22+

## Integration Points

### Cross-Origin Setup

- Frontend runs on Quasar dev server (typically :9000)
- Backend runs on Django dev server (:8000)
- Axios configured in `src/boot/axios.ts` for API communication

### Build Targets

- Browser: ES2022, Firefox 115+, Chrome 115+, Safari 14+
- Node: v22 (see `package.json` engines)

## Environment Setup

### Backend Environment

- **Anaconda Path**: `D:\Software\anaconda3`
- **Conda Environment**: `ling-task-flow-backend`
- **Activation**: `conda activate ling-task-flow-backend`

### Frontend Environment

- **Node.js**: v22
- **Package Manager**: npm (not yarn)
- **Dev Server**: Typically runs on port 9000

## Getting Started Checklist

1. **Backend**: Activate conda environment (`conda activate ling-task-flow-backend`), run migrations, create superuser
2. **Frontend**: Install dependencies (`npm install`), start dev server
3. **Database**: SQLite file will be created automatically
4. **API**: Currently no API endpoints defined - add to `LingTaskFlow/views.py` and `urls.py`

## Common Patterns to Follow

- **Models**: Define in `LingTaskFlow/models.py`
- **Views**: Use Django REST Framework patterns when adding API endpoints
- **Frontend Components**: Use Quasar components with TypeScript
- **State Management**: Pinia stores with composition API style
- **Internationalization**: i18n setup ready in `src/i18n/`

提醒的内容：

1.  后端已经集成了 API 文档自动生成(drf-spectacular)，如果前端开发过程中需要调用后端的接口，可以查阅 API 文档地址：http://127.0.0.1:8000/api/docs/
2.  每一次任务完成后都需要确认该任务已完成并在任务列表中打勾 ✅
3.  在完成每一次任务之后，将报告写入 `report` 文件夹中，而不是 `docs` 中
4.  汇总已经开发完成的任务，然后你需要给出下一次的任务，并询问用户是否继续
5.  项目的前后端已经启动，你不需要调用命令再次启动
