# File to Markdown Platform

Browser-based file-to-Markdown conversion MVP.

## Current scope

- Supported input formats: `docx`, `pdf`, `xlsx`
- Out of scope in this phase: `pptx`
- Current processing mode: API background task after upload (MVP mode)

## Delivered capabilities

- Upload API with server-side extension allow-list validation.
- Signature checks for uploaded files (`pdf`, `docx`, `xlsx`).
- Task creation with per-task access token.
- Status polling endpoint protected by `X-Access-Token`.
- Conversion routing for `docx`/`pdf`/`xlsx`.
- Markdown preview in task status payload.
- Frontend upload + polling + preview + download flow.
- Audit metadata model and retention helpers.

## Architecture snapshot

- Backend: FastAPI (Python 3.13.12)
- Frontend: React + Vite
- Runtime orchestration: Docker Compose
- Storage: local volume-backed filesystem (`STORAGE_DIR`)
- Data stores in compose: PostgreSQL + Redis (prepared for next stage integration)

## Quick start

### Local Python workflow

Install dependencies:

```bash
python -m pip install -e ".[dev]"
```

Run backend tests:

```bash
pytest -q
```

Start API:

```bash
uvicorn backend.app.main:app --reload
```

Health check endpoint:

```text
GET /
```

### Docker Compose workflow

Start services:

```bash
docker compose up --build
```

Default exposed endpoints:

- Frontend: `http://localhost:4173`
- API: `http://localhost:8000`
- PostgreSQL: `localhost:5432`
- Redis: `localhost:6379`

## API endpoints (MVP)

### `POST /api/upload`

- Multipart field: `file`
- Returns:
  - `task_id`
  - `access_token`

### `GET /api/tasks/{task_id}`

- Required request header: `X-Access-Token`
- Returns task metadata, status, and optional `markdown` preview.

## Security controls (current)

- Upload extension allow-list for `docx`, `pdf`, `xlsx`.
- File signature checks before conversion.
- Upload payload size cap (`MAX_UPLOAD_BYTES`).
- Per-IP upload rate limiting:
  - `UPLOAD_RATE_LIMIT_MAX_REQUESTS`
  - `UPLOAD_RATE_LIMIT_WINDOW_SECONDS`
- Access token required for task query.
- Access token expiration (`ACCESS_TOKEN_TTL_SECONDS`).
- Audit record policy:
  - keep metadata and processing state
  - do not persist full Markdown content in audit logs

## Core environment variables

- `APP_HOST` (default `0.0.0.0`)
- `APP_PORT` (default `8000`)
- `STORAGE_DIR` (default `storage`)
- `MAX_UPLOAD_BYTES` (default `20971520`)
- `UPLOAD_RATE_LIMIT_MAX_REQUESTS` (default `20`)
- `UPLOAD_RATE_LIMIT_WINDOW_SECONDS` (default `60`)
- `ACCESS_TOKEN_TTL_SECONDS` (default `86400`)
- `TASK_STORE_TTL_SECONDS` (default `3600`)
- `TASK_STORE_MAX_ITEMS` (default `2000`)
- `MARKDOWN_PREVIEW_MAX_CHARS` (default `20000`)

See `.env.example` for a runnable baseline.

## Verification checklist

- Backend tests:
  - `pytest -q`
- Frontend build:
  - `cd frontend && npm run build`
- Frontend e2e:
  - `cd frontend && npm run test:e2e -- --reporter=line`
- Dependency audit:
  - `cd frontend && npm audit --json`

## Documentation index

- Design spec: `docs/superpowers/specs/2026-03-25-file-to-md-design.md`
- Implementation plan: `docs/plans/2026-03-25-file-to-md-platform.md`
- Delivery retrospective: `docs/plans/2026-03-26-project-implementation-retrospective.md`

## Known limitations (MVP)

- Task state is currently in-memory and not durable across API restarts.
- Conversion execution uses API background tasks instead of dedicated distributed workers.
- Rate limiting is local-process level, not globally shared across instances.
