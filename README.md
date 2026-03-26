# File to Markdown Platform

Minimal scaffold for a browser-based file-to-Markdown conversion service.

## Prerequisites

- Python 3.13.12
- Docker and Docker Compose

## Local development

Install dependencies:

```bash
python -m pip install -e ".[dev]"
```

Run the smoke test:

```bash
pytest backend/tests/test_smoke.py -v
```

Start the API locally:

```bash
uvicorn backend.app.main:app --reload
```

The root endpoint returns a simple health payload at `GET /`.

## Docker Compose

Start the full stack:

```bash
docker compose up --build
```

Services exposed by default:

- Frontend: `http://localhost:4173`
- API: `http://localhost:8000`
- PostgreSQL: `localhost:5432`
- Redis: `localhost:6379`

Note: in the current MVP, conversion is triggered as an API background task after upload.

## Audit and retention

- Audit records keep task metadata, IP, device ID, and processing status.
- Full Markdown output is not written into audit logs.
- Conversion outputs and temporary artifacts can be cleaned with the retention helpers in `backend/app/services/retention.py`.

## Security controls (MVP)

- Upload endpoint enforces:
  - extension allow-list (`docx`, `pdf`, `xlsx`)
  - file-signature checks
  - size limit (`MAX_UPLOAD_BYTES`)
  - per-IP request throttling (`UPLOAD_RATE_LIMIT_MAX_REQUESTS` within `UPLOAD_RATE_LIMIT_WINDOW_SECONDS`)
- Task query endpoint requires `X-Access-Token`.
- Access tokens expire after `ACCESS_TOKEN_TTL_SECONDS`.
