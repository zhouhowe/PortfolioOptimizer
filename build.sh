#!/bin/bash
set -e

echo "========================================"
echo "Starting Build Process"
echo "========================================"

# Backend Tests
echo "[1/2] Running Backend Tests..."
cd backend
if [ -f "uv.lock" ]; then
    uv sync
fi
uv run pytest tests/
cd ..

# Frontend Build (includes tests)
echo "[2/2] Building Frontend (with Tests)..."
cd frontend
npm install
npm run build
cd ..

echo "========================================"
echo "Build Process Completed Successfully!"
echo "========================================"
