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

You can also start using the compatibility module path expected by some orchestrators:
```
uvicorn main:app --host 0.0.0.0 --port 3000
```

### One-line startup without a pre-created virtualenv
This repository includes a helper script that installs requirements (if missing) and starts the service:
```
./run.sh
```
You can override the port via environment variable (defaults to 3000 if unset):
```
PORT=3000 ./run.sh
```

### Environment variables
Copy `.env.example` to `.env` and adjust as needed:
```
cp .env.example .env
# Edit .env to change the port; default is 3000
```
The service uses:
- `PORT` — listening port for the API (default 3000)

## Notes
- CORS is permissive for development and can be restricted later.
- The preview/start mechanism in your environment can import `app.main:app` directly.
- Correct Uvicorn import path: `app.main:app` is preferred, and a compatibility shim at `main.py` ensures `uvicorn main:app` also works if your orchestrator uses that path.
