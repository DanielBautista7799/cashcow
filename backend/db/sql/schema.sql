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