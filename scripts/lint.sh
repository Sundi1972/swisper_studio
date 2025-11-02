#!/bin/bash
# Lint backend code
# Run this before committing to catch import errors early!

set -e

echo "🔍 Running linters on backend code..."
echo ""

cd "$(dirname "$0")/../backend"

echo "1️⃣ Checking imports and unused code (ruff)..."
docker compose -f ../docker-compose.yml exec backend bash -c "
  uv pip install --quiet ruff && \
  ruff check app/ --select F401,F811,E402,F821 || true
"

echo ""
echo "2️⃣ Checking type hints (mypy)..."
docker compose -f ../docker-compose.yml exec backend bash -c "
  uv pip install --quiet mypy && \
  mypy app/main.py app/api/ app/models/ --ignore-missing-imports || true
"

echo ""
echo "3️⃣ Checking code format (ruff format)..."
docker compose -f ../docker-compose.yml exec backend bash -c "
  ruff format --check app/ || true
"

echo ""
echo "✅ Linting complete!"
echo ""
echo "To auto-fix issues:"
echo "  ruff check --fix app/"
echo "  ruff format app/"

