#!/usr/bin/env bash
# Simple launcher for PhysicalLayerService that:
# - Installs dependencies if missing
# - Starts uvicorn with the correct app import path
# - Does not require a pre-created virtual environment
# - Binds to 0.0.0.0 and defaults to port 3000 (overridable via PORT env or .env)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Ensure Python is available
if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 not found in PATH. Please install Python 3.9+." >&2
  exit 1
fi

# Use python3 -m pip to avoid pip PATH confusion
PIP="python3 -m pip"

# Upgrade pip silently if possible (non-fatal if fails)
$PIP install --upgrade --quiet pip setuptools wheel || true

# Install dependencies if uvicorn or fastapi is missing
NEED_INSTALL=0
python3 - <<'PYCHECK' || NEED_INSTALL=1
try:
    import fastapi  # noqa: F401
    import uvicorn  # noqa: F401
except Exception:
    raise
PYCHECK

if [ "$NEED_INSTALL" -ne 0 ]; then
  echo "Installing dependencies from requirements.txt..."
  $PIP install -r requirements.txt
fi

# Determine port, default 3000
PORT="${PORT:-3000}"

# Run uvicorn with the correct app path
exec python3 -m uvicorn app.main:app --host 0.0.0.0 --port "$PORT"
