CREATE TYPE atm_status AS ENUM('Operational', 'In-Transport', 'Maintenance', 'Offline');
CREATE TYPE service_call_priority AS ENUM('Low','Medium', 'Critical');
CREATE TYPE service_call_status AS ENUM('Pending', 'In-Progress', 'Completed', 'Failed');
CREATE TYPE user_role AS ENUM('Admin', 'Technician', 'Auditor');

CREATE TABLE branches(
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    location_region VARCHAR(50) NOT NULL ,
    capacity INTEGER NOT NULL,
    supervisor_id INTEGER NOT NULL
);

CREATE TABLE technicians(
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    branch_id INTEGER references branches(id)

);

CREATE TABLE atms (
    id SERIAL PRIMARY KEY,
    serial_number VARCHAR(100) NOT NULL UNIQUE,
    model VARCHAR(100) NOT NULL,
    status atm_status NOT NULL,
    cash_level NUMERIC(5,2) NOT NULL check(cash_level BETWEEN 0 AND 100),
    branch_id INTEGER NOT NULL references branches(id)
);

CREATE TABLE service_calls(
    id SERIAL PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    priority service_call_priority NOT NULL,
    status service_call_status NOT NULL,
    atm_id INTEGER NOT NULL references atms(id),
    technician_id INTEGER NOT NULL references technicians(id)
);

CREATE TABLE diagnostic_reports(
    id SERIAL PRIMARY KEY,
    service_call_id INTEGER NOT NULL references service_calls(id),
    file_url TEXT NOT NULL,
    notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE users(
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    role user_role NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE refresh_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    token_hash VARCHAR(64) UNIQUE NOT NULL,
    chain_id VARCHAR(36) NOT NULL,
    issued_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL,
    revoked BOOLEAN DEFAULT FALSE
);

CREATE INDEX refresh_tokens_token_hash_idx
ON refresh_tokens(token_hash);

CREATE INDEX refresh_tokens_chain_id_idx
ON refresh_tokens(chain_id);

-- Server-side pagination indexes
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
