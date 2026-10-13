ALTER TABLE atms
ADD COLUMN IF NOT EXISTS
is_active BOOLEAN NOT NULL DEFAULT TRUE;

ALTER TABLE atms
ADD COLUMN IF NOT EXISTS
deleted_at TIMESTAMPTZ;

ALTER TABLE atms
ADD COLUMN IF NOT EXISTS
deleted_by INTEGER;

ALTER TABLE service_calls
ADD COLUMN IF NOT EXISTS
is_active BOOLEAN NOT NULL DEFAULT TRUE;

ALTER TABLE service_calls
ADD COLUMN IF NOT EXISTS
deleted_at TIMESTAMPTZ;

ALTER TABLE service_calls
ADD COLUMN IF NOT EXISTS
deleted_by INTEGER;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'atms_deleted_by_fkey'
    ) THEN
        ALTER TABLE atms
        ADD CONSTRAINT atms_deleted_by_fkey
        FOREIGN KEY (deleted_by)
        REFERENCES users(id);
    END IF;
END
$$;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname =
            'service_calls_deleted_by_fkey'
    ) THEN
        ALTER TABLE service_calls
        ADD CONSTRAINT
            service_calls_deleted_by_fkey
        FOREIGN KEY (deleted_by)
        REFERENCES users(id);
    END IF;
END
$$;

CREATE TABLE IF NOT EXISTS audit_entries (
    id SERIAL PRIMARY KEY,
    record_type VARCHAR(50) NOT NULL,
    record_id INTEGER NOT NULL,
    action VARCHAR(50) NOT NULL,
    acting_user_id INTEGER NOT NULL
        REFERENCES users(id),
    created_at TIMESTAMPTZ
        NOT NULL DEFAULT NOW(),
    changes JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS
audit_entries_record_idx
ON audit_entries(
    record_type,
    record_id,
    created_at
);

CREATE INDEX IF NOT EXISTS
atms_is_active_idx
ON atms(is_active);

CREATE INDEX IF NOT EXISTS
service_calls_is_active_idx
ON service_calls(is_active);
