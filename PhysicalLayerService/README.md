# PhysicalLayerService

FastAPI service implementing Physical Layer control and telemetry for the SDA Satellite Link project.

## Features
- Health and version endpoints
- Pydantic BaseSettings with .env support
- CORS configured
- Structured logging
- Dockerized with Python slim

## Run locally

1. Create and populate `.env` (see `.env.example`).
2. Install dependencies (venv optional):
   ```bash
   pip install -r requirements.txt
   ```
   If you prefer a venv:
   ```bash
   python -m venv .venv
   . .venv/bin/activate
   pip install -r requirements.txt
   ```
3. Start the service (choose one):
   - Using uvicorn module (recommended):
     ```bash
     python -m uvicorn app.main:app --host 0.0.0.0 --port 3000
     ```
   - Using provided script:
     ```bash
     HOST=0.0.0.0 PORT=3000 ./run.sh
     ```
   - Using Python:
     ```bash
     python -m app.main
     ```
     or
     ```bash
     python app/server.py
     ```

The app will listen on `0.0.0.0:${PORT}` (default 3000).

### Preview/CI runner note
Some runners invoke from the repo root using:
```bash
uvicorn main:app --host 0.0.0.0 --port 3000
```
This repository includes a root-level `main.py` shim that exposes `main:app` and imports from `PhysicalLayerService/app/main.py`, so the above command works without activating a virtualenv or modifying PYTHONPATH.

Dependency install note:
- Preview/CI typically installs dependencies from the container root `requirements.txt`. That file includes `pydantic-settings>=2,<3`, `pydantic>=2,<3`, `fastapi`, `uvicorn`, and `python-dotenv`.
- A minimal runtime shim is present in `app/core/config.py` to avoid startup failure if `pydantic-settings` is missing; however, you should ensure it is installed for full functionality.

## Endpoints
- `GET /health` -> 200 OK with status and timestamp
- `GET /version` -> service name and semantic version
- `GET /` -> basic links

Interactive docs at `/docs` and OpenAPI at `/openapi.json`.

## Docker

Build and run:
```bash
docker build -t physical-layer-service:latest .
docker run -it --rm -p 3000:3000 --env PORT=3000 --name pls physical-layer-service:latest
```

## Environment variables
See `.env.example` for configurable settings.
