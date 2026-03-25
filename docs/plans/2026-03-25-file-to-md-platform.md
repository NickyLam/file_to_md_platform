# File to Markdown Platform Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a browser-based file-to-Markdown service that converts `docx`, `pdf`, and `xlsx` files into structured Markdown with async processing, audit logging, and optional OCR/model enhancement.

**Architecture:** Use a Python FastAPI backend with Redis-backed background jobs and PostgreSQL for task metadata and audit logs. Keep conversion logic isolated by file type, store uploaded files and generated Markdown on disk-backed volumes, and expose a small web UI for upload, status polling, preview, and download.

**Tech Stack:** Python 3.13.12, FastAPI, Redis, PostgreSQL, Docker Compose, pytest, Playwright, a frontend stack suitable for the repo's chosen UI layer.

---

### Task 1: Scaffold the service repository

**Files:**
- Create: `pyproject.toml`
- Create: `README.md`
- Create: `docker-compose.yml`
- Create: `.env.example`
- Create: `backend/app/__init__.py`
- Create: `backend/app/main.py`
- Create: `backend/tests/test_smoke.py`

**Step 1: Write the failing test**

```python
def test_app_imports():
    import backend.app.main
```

**Step 2: Run test to verify it fails**

Run: `pytest backend/tests/test_smoke.py -v`
Expected: FAIL because the package layout does not exist yet.

**Step 3: Write minimal implementation**

- Add the Python package structure.
- Create a minimal FastAPI app that imports cleanly.
- Add a root health endpoint.

**Step 4: Run test to verify it passes**

Run: `pytest backend/tests/test_smoke.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add pyproject.toml README.md docker-compose.yml .env.example backend/
git commit -m "chore: scaffold file to markdown service"
```

### Task 2: Add task model, database migration, and audit log schema

**Files:**
- Create: `backend/app/db.py`
- Create: `backend/app/models.py`
- Create: `backend/app/repositories/tasks.py`
- Create: `backend/app/repositories/audit.py`
- Create: `backend/migrations/001_init.sql`
- Create: `backend/tests/test_models.py`

**Step 1: Write the failing test**

```python
def test_task_record_has_required_fields():
    task = TaskRecord(...)
    assert task.status in {"pending", "running", "success", "failed", "success_with_warnings"}
```

**Step 2: Run test to verify it fails**

Run: `pytest backend/tests/test_models.py -v`
Expected: FAIL because the task model and schema are missing.

**Step 3: Write minimal implementation**

- Define task metadata fields.
- Define audit log fields.
- Add the initial SQL schema.

**Step 4: Run test to verify it passes**

Run: `pytest backend/tests/test_models.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add backend/app/db.py backend/app/models.py backend/app/repositories backend/migrations/001_init.sql backend/tests/test_models.py
git commit -m "feat: add task and audit schemas"
```

### Task 3: Implement upload, validation, and task creation API

**Files:**
- Create: `backend/app/api/uploads.py`
- Create: `backend/app/api/tasks.py`
- Modify: `backend/app/main.py`
- Create: `backend/tests/test_upload_api.py`

**Step 1: Write the failing test**

```python
def test_upload_rejects_unsupported_extension(client):
    response = client.post("/api/upload", files={"file": ("a.exe", b"x")})
    assert response.status_code == 400
```

**Step 2: Run test to verify it fails**

Run: `pytest backend/tests/test_upload_api.py -v`
Expected: FAIL because the route does not exist yet.

**Step 3: Write minimal implementation**

- Add upload endpoint.
- Revalidate file type on the server.
- Compute file hash.
- Persist task metadata.
- Return `task_id` and `access_token`.

**Step 4: Run test to verify it passes**

Run: `pytest backend/tests/test_upload_api.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add backend/app/main.py backend/app/api/uploads.py backend/app/api/tasks.py backend/tests/test_upload_api.py
git commit -m "feat: add upload and task creation api"
```

### Task 4: Implement async worker, conversion routing, and result storage

**Files:**
- Create: `backend/app/worker.py`
- Create: `backend/app/converters/base.py`
- Create: `backend/app/converters/docx.py`
- Create: `backend/app/converters/pdf.py`
- Create: `backend/app/converters/xlsx.py`
- Create: `backend/app/services/storage.py`
- Create: `backend/tests/test_converters.py`

**Step 1: Write the failing test**

```python
def test_docx_converter_returns_markdown():
    result = convert_docx(sample_path)
    assert "# " in result.markdown
```

**Step 2: Run test to verify it fails**

Run: `pytest backend/tests/test_converters.py -v`
Expected: FAIL because converters are not implemented yet.

**Step 3: Write minimal implementation**

- Implement converter interfaces.
- Add routing by file type.
- Save generated Markdown and intermediate status updates.

**Step 4: Run test to verify it passes**

Run: `pytest backend/tests/test_converters.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add backend/app/worker.py backend/app/converters backend/app/services/storage.py backend/tests/test_converters.py
git commit -m "feat: add conversion pipeline"
```

### Task 5: Add access control, task status polling, and partial-success semantics

**Files:**
- Create: `backend/app/api/status.py`
- Modify: `backend/app/api/tasks.py`
- Create: `backend/tests/test_access_control.py`

**Step 1: Write the failing test**

```python
def test_status_requires_access_token(client):
    response = client.get("/api/tasks/123")
    assert response.status_code == 401
```

**Step 2: Run test to verify it fails**

Run: `pytest backend/tests/test_access_control.py -v`
Expected: FAIL because status access control is not enforced yet.

**Step 3: Write minimal implementation**

- Require `access_token` for status, preview, and download.
- Enforce `success_with_warnings` for degraded but usable outputs.
- Return `failed` when no usable Markdown exists.

**Step 4: Run test to verify it passes**

Run: `pytest backend/tests/test_access_control.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add backend/app/api/status.py backend/app/api/tasks.py backend/tests/test_access_control.py
git commit -m "feat: secure task access and status semantics"
```

### Task 6: Build the web UI for upload, polling, preview, and download

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/src/App.tsx`
- Create: `frontend/src/components/UploadForm.tsx`
- Create: `frontend/src/components/TaskStatus.tsx`
- Create: `frontend/src/components/MarkdownPreview.tsx`
- Create: `frontend/tests/upload-flow.spec.ts`

**Step 1: Write the failing test**

```ts
test("user can upload and see a task", async ({ page }) => {
  await page.goto("/");
  await page.setInputFiles("input[type=file]", "fixtures/sample.docx");
  await expect(page.getByText(/pending|running|success/i)).toBeVisible();
});
```

**Step 2: Run test to verify it fails**

Run: `npx playwright test frontend/tests/upload-flow.spec.ts`
Expected: FAIL because the UI does not exist yet.

**Step 3: Write minimal implementation**

- Add upload UI.
- Poll task status.
- Show rendered Markdown preview.
- Add download control.

**Step 4: Run test to verify it passes**

Run: `npx playwright test frontend/tests/upload-flow.spec.ts`
Expected: PASS.

**Step 5: Commit**

```bash
git add frontend/package.json frontend/src frontend/tests/upload-flow.spec.ts
git commit -m "feat: add web upload and preview flow"
```

### Task 7: Add observability, retention controls, and end-to-end verification

**Files:**
- Create: `backend/tests/test_audit_logging.py`
- Create: `backend/tests/test_retention.py`
- Create: `backend/tests/test_e2e_conversion.py`
- Modify: `README.md`

**Step 1: Write the failing test**

```python
def test_audit_log_never_stores_full_markdown():
    record = build_audit_record(...)
    assert record.markdown_text is None
```

**Step 2: Run test to verify it fails**

Run: `pytest backend/tests/test_audit_logging.py backend/tests/test_retention.py backend/tests/test_e2e_conversion.py -v`
Expected: FAIL because the audit and retention behaviors are not finished yet.

**Step 3: Write minimal implementation**

- Record IP, `device_id`, file hash, and metadata only.
- Add configurable cleanup for raw files, results, and temporary artifacts.
- Add a small end-to-end conversion test for each supported file type.

**Step 4: Run test to verify it passes**

Run: `pytest backend/tests/test_audit_logging.py backend/tests/test_retention.py backend/tests/test_e2e_conversion.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add backend/tests/test_audit_logging.py backend/tests/test_retention.py backend/tests/test_e2e_conversion.py README.md
git commit -m "feat: add audit retention and end-to-end coverage"
```

### Task 8: Verify the full stack with Docker Compose

**Files:**
- Modify: `docker-compose.yml`
- Modify: `README.md`

**Step 1: Write the failing test**

```bash
docker compose up --build
```

Expected: fail until all services, env vars, and ports are wired correctly.

**Step 2: Run the full stack**

Run: `docker compose up --build`
Expected: backend, worker, Redis, PostgreSQL, and frontend all start cleanly.

**Step 3: Write minimal implementation**

- Fix environment wiring.
- Verify network connectivity between services.
- Ensure storage volumes persist generated files.

**Step 4: Run the full stack again**

Run: `docker compose up --build`
Expected: all services healthy and the upload flow works end to end.

**Step 5: Commit**

```bash
git add docker-compose.yml README.md
git commit -m "chore: verify containerized deployment"
```

