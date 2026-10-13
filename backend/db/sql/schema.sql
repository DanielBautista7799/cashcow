CREATE TYPE atm_status AS ENUM(
    'Operational',
    'In-Transport',
    'Maintenance',
    'Offline'
);

CREATE TYPE service_call_priority AS ENUM(
    'Low',
    'Medium',
    'Critical'
);

CREATE TYPE service_call_status AS ENUM(
    'Pending',
    'In-Progress',
    'Completed',
    'Failed'
);

CREATE TYPE user_role AS ENUM(
    'Admin',
    'Technician',
    'Auditor'
);

CREATE TABLE branches(
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    location_region VARCHAR(50) NOT NULL,
    capacity INTEGER NOT NULL,
    supervisor_id INTEGER NOT NULL
);

CREATE TABLE technicians(
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    branch_id INTEGER
        REFERENCES branches(id)
);

CREATE TABLE atms (
    id SERIAL PRIMARY KEY,
    serial_number VARCHAR(100)
        NOT NULL UNIQUE,
    model VARCHAR(100) NOT NULL,
    status atm_status NOT NULL,
    cash_level NUMERIC(5,2)
        NOT NULL
        CHECK(
            cash_level BETWEEN 0 AND 100
        ),
    branch_id INTEGER NOT NULL
        REFERENCES branches(id),
    is_active BOOLEAN
        NOT NULL DEFAULT TRUE,
    deleted_at TIMESTAMPTZ,
    deleted_by INTEGER
);

CREATE TABLE service_calls(
    id SERIAL PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    priority service_call_priority NOT NULL,
    status service_call_status NOT NULL,
    atm_id INTEGER NOT NULL
        REFERENCES atms(id),
    technician_id INTEGER NOT NULL
        REFERENCES technicians(id),
    is_active BOOLEAN
        NOT NULL DEFAULT TRUE,
    deleted_at TIMESTAMPTZ,
    deleted_by INTEGER
);

CREATE TABLE diagnostic_reports(
    id SERIAL PRIMARY KEY,
    service_call_id INTEGER NOT NULL
        REFERENCES service_calls(id),
    file_url TEXT NOT NULL,
    notes TEXT,
    created_at TIMESTAMP
        NOT NULL DEFAULT NOW()
);

CREATE TABLE users(
    id SERIAL PRIMARY KEY,
    username VARCHAR(50)
        NOT NULL UNIQUE,
    hashed_password VARCHAR(255)
        NOT NULL,
    role user_role NOT NULL,
    is_active BOOLEAN
        NOT NULL DEFAULT TRUE
);

ALTER TABLE atms
ADD CONSTRAINT atms_deleted_by_fkey
FOREIGN KEY (deleted_by)
REFERENCES users(id);

ALTER TABLE service_calls
ADD CONSTRAINT service_calls_deleted_by_fkey
FOREIGN KEY (deleted_by)
REFERENCES users(id);

CREATE TABLE refresh_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL
        REFERENCES users(id),
    token_hash VARCHAR(64)
        UNIQUE NOT NULL,
    chain_id VARCHAR(36) NOT NULL,
    issued_at TIMESTAMPTZ
        DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL,
    revoked BOOLEAN DEFAULT FALSE
);

CREATE TABLE audit_entries (
    id SERIAL PRIMARY KEY,
    record_type VARCHAR(50) NOT NULL,
    record_id INTEGER NOT NULL,
    action VARCHAR(50) NOT NULL,
    acting_user_id INTEGER NOT NULL
        REFERENCES users(id),
    created_at TIMESTAMPTZ
        NOT NULL DEFAULT NOW(),
    changes JSONB
        NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX refresh_tokens_token_hash_idx
ON refresh_tokens(token_hash);

CREATE INDEX refresh_tokens_chain_id_idx
ON refresh_tokens(chain_id);

CREATE INDEX IF NOT EXISTS atms_status_idx
ON atms(status);

CREATE INDEX IF NOT EXISTS atms_branch_id_idx
ON atms(branch_id);

CREATE INDEX IF NOT EXISTS atms_model_idx
ON atms(model);

CREATE INDEX IF NOT EXISTS service_calls_status_idx
ON service_calls(status);

CREATE INDEX IF NOT EXISTS service_calls_atm_id_idx
ON service_calls(atm_id);

CREATE INDEX IF NOT EXISTS atms_is_active_idx
ON atms(is_active);

CREATE INDEX IF NOT EXISTS
service_calls_is_active_idx
ON service_calls(is_active);

CREATE INDEX IF NOT EXISTS
audit_entries_record_idx
ON audit_entries(
    record_type,
    record_id,
    created_at
);
