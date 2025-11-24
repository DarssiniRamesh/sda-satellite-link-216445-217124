# PhysicalLayerService

Minimal FastAPI scaffolding for the Physical Layer Service.

## Endpoints
- GET `/` -> `{ "name": "PhysicalLayerService", "status": "running" }`
- GET `/health` -> `{ "status": "ok" }`
- GET `/info` -> metadata including effective port and env

## Run locally

Install dependencies:
```
pip install -r requirements.txt
```

Start the service (default port 3000 on 0.0.0.0):
```
uvicorn app.main:app --host 0.0.0.0 --port 3000
```

Or using the Python entry point that honors the `PORT` env var:
```
export PORT=3000
python -m app.main
```

## Notes
- CORS is permissive for development and can be restricted later.
- The preview/start mechanism in your environment can import `app.main:app` directly.
