#!/usr/bin/env bash

# CashCow Command Center
# Sets up a fresh clone of the project.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "== CashCow Setup =="

for command in python3 npm psql; do
    if ! command -v "$command" >/dev/null; then
        echo "Missing prerequisite: $command"
        exit 1
    fi
done

cd "$ROOT_DIR"

# Create the virtual environment if it does not already exist.
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

source .venv/bin/activate

echo "Installing backend dependencies..."
pip install -r requirements.txt

# Never overwrite an existing environment file.
if [ -f "backend/.env" ]; then
    echo "backend/.env already exists."
else
    echo "backend/.env is missing. Create it before running the backend."
fi

cd frontend

echo "Installing frontend dependencies..."
npm install

echo "Setup complete."
