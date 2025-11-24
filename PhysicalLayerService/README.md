# PhysicalLayerService

Minimal FastAPI scaffolding providing health and root endpoints.

## Endpoints
- GET `/` — service metadata
- GET `/health` — health probe

## Run locally

The preview system manages ports automatically, but for local runs:

```bash
pip install -r requirements.txt

# Option A: Using the thin top-level entrypoint (matches orchestrators):
uvicorn main:app --host 0.0.0.0 --port "${PORT:-8000}"

# Option B: Direct module path:
uvicorn src.api.main:app --host 0.0.0.0 --port "${PORT:-8000}"
```

Environment variables:
- `PORT` (optional, not bound by app code; preview manages ports)
- `CORS_ALLOW_ORIGINS` (comma-separated origins, default: *)
