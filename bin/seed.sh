#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

RESET=false
YES=false

for arg in "$@"; do
    case "$arg" in
        --reset)
            RESET=true
            ;;
        --yes)
            YES=true
            ;;
        *)
            echo "Unknown option: $arg"
            exit 1
            ;;
    esac
done

# Load backend environment variables
if [ -f "$ROOT_DIR/backend/.env" ]; then
    set -a
    source "$ROOT_DIR/backend/.env"
    set +a
fi

if [ -z "${DATABASE_URL:-}" ]; then
    echo "DATABASE_URL is missing."
    exit 1
fi

# psql cannot use the SQLAlchemy +asyncpg part
PSQL_URL="${DATABASE_URL/+asyncpg/}"

echo "== CashCow Seed =="

# Make sure the database is reachable before changing anything
if ! psql "$PSQL_URL" -c "SELECT 1;" >/dev/null 2>&1; then
    echo "Database is unreachable."
    exit 1
fi

# Create schema only if it does not already exist
TABLE_EXISTS=$(psql "$PSQL_URL" -tAc "SELECT to_regclass('public.branches');")

if [ -z "$TABLE_EXISTS" ]; then
    echo "Creating database schema..."
    psql "$PSQL_URL" \
        -v ON_ERROR_STOP=1 \
        -f "$ROOT_DIR/backend/db/sql/schema.sql"
else
    echo "Database schema already exists."
fi

# Reset existing seed data when requested
if [ "$RESET" = true ]; then

    if [ "$YES" = false ]; then
        read -r -p "Reset all CashCow seed data? [y/N] " answer

        if [ "$answer" != "y" ] && [ "$answer" != "Y" ]; then
            echo "Reset cancelled."
            exit 0
        fi
    fi

    echo "Resetting seed data..."

    psql "$PSQL_URL" \
        -v ON_ERROR_STOP=1 \
        -c "TRUNCATE TABLE diagnostic_reports, service_calls, atms, technicians, branches, users RESTART IDENTITY CASCADE;"
fi

# Do not seed the same data twice
if [ "$RESET" = false ]; then
    SEEDED=$(psql "$PSQL_URL" -tAc \
        "SELECT 1 FROM branches WHERE id = 1 LIMIT 1;")

    if [ "$SEEDED" = "1" ]; then
        echo "Database is already seeded."
        exit 0
    fi
fi

echo "Loading CashCow data..."

psql "$PSQL_URL" \
    -v ON_ERROR_STOP=1 \
    -f "$ROOT_DIR/backend/db/sql/seed.sql"

echo "Loading demo users..."

cd "$ROOT_DIR/backend"
"$ROOT_DIR/.venv/bin/python" -m scripts.seed_users

echo "Seed complete."