# Project Repository

This is the initial README file for the project.

## Services

- PhysicalLayerService (FastAPI)
  - Path: `PhysicalLayerService/`
  - App import: `app.main:app`
  - Default port: 3000 (overridable via `PORT` env var)
  - Health: `GET /health` -> `{"status":"ok"}`
  - Quick start:
    ```
    cd PhysicalLayerService
    pip install -r requirements.txt
    uvicorn app.main:app --host 0.0.0.0 --port 3000
    ```