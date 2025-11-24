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
2. Create virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   . .venv/bin/activate
   pip install -r requirements.txt
   ```
3. Start the service:
   ```bash
   python -m app.main
   ```
   or
   ```bash
   python app/server.py
   ```

The app will listen on `0.0.0.0:${PORT}` (default 3000).

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
