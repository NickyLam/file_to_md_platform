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

## Audit and retention

- Audit records keep task metadata, IP, device ID, and processing status.
- Full Markdown output is not written into audit logs.
- Conversion outputs and temporary artifacts can be cleaned with the retention helpers in `backend/app/services/retention.py`.
