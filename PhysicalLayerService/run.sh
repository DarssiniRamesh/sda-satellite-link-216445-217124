#!/usr/bin/env bash
# Simple runner for PhysicalLayerService without requiring virtualenv activation.
# Usage: HOST=0.0.0.0 PORT=3000 ./run.sh

set -euo pipefail

HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-3000}"

# Prefer running via module path to ensure proper imports
exec python -m uvicorn app.main:app --host "$HOST" --port "$PORT"
