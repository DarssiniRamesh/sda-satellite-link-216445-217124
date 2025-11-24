# Project Repository

This is the initial README file for the project.

## Services

- PhysicalLayerService (FastAPI)
  - Path: `PhysicalLayerService/`
  - App import: Preferred `app.main:app` (also supports `main:app` for compatibility)
  - Default port: 3000 (overridable via `PORT` env var)
  - Health: `GET /health` -> `{"status":"ok"}`
  - Quick start:
    ```
    cd PhysicalLayerService
    pip install -r requirements.txt
    uvicorn app.main:app --host 0.0.0.0 --port 3000
    ```
    If your environment attempts `uvicorn main:app`, it will also work due to a compatibility shim.
  - One-line start without venv:
    ```
    cd PhysicalLayerService
    ./run.sh           # defaults to PORT=3000, use PORT=xxxx to override
    ```