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
