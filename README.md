# SDA Satellite Link - Monorepo

This repository contains multiple backend services. This step scaffolds the PhysicalLayerService.

- PhysicalLayerService (FastAPI) located at `./PhysicalLayerService`
  - Start locally:
    - From repo root (preview/CI compatible):
      ```bash
      uvicorn main:app --host 0.0.0.0 --port 3000
      ```
    - From service directory:
      ```bash
      cd PhysicalLayerService
      python -m uvicorn app.main:app --host 0.0.0.0 --port 3000
      # or
      ./run.sh
      ```
  - Health: GET http://localhost:3000/health
  - Version: GET http://localhost:3000/version

Notes:
- The root-level `main.py` is a lightweight shim that imports the FastAPI `app` from `PhysicalLayerService/app/main.py`, ensuring `uvicorn main:app` works without a virtualenv.
- Preview/CI installers typically run `pip install -r requirements.txt` from the container root. The container root `requirements.txt` includes `pydantic-settings>=2,<3` and related dependencies required for startup.