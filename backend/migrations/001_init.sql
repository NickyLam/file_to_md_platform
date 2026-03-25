CREATE TABLE tasks (
    task_id TEXT PRIMARY KEY,
    file_hash TEXT NOT NULL,
    file_name TEXT NOT NULL,
    file_size BIGINT NOT NULL,
    file_type TEXT NOT NULL,
    status TEXT NOT NULL,
    access_token TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    CONSTRAINT tasks_status_check CHECK (
        status IN (
            'pending',
            'running',
            'success',
            'failed',
            'success_with_warnings'
        )
    )
);

CREATE TABLE audit_logs (
    audit_id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL REFERENCES tasks(task_id),
    event_type TEXT NOT NULL,
    ip_address TEXT NOT NULL,
    device_id TEXT NOT NULL,
    file_hash TEXT NOT NULL,
    task_status TEXT NOT NULL,
    duration_ms BIGINT,
    failure_reason_code TEXT,
    engine_version TEXT,
    ocr_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    model_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL
);
