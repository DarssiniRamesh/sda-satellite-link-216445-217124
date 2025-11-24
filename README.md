# Project Repository

This is the initial README file for the project.

## Running PhysicalLayerService

The PhysicalLayerService FastAPI app supports an environment variable `PORT` and binds to `0.0.0.0`. Allowed ports are: 3000, 3001, 3002, 5000. If `PORT` is not set or invalid, it defaults to `5000`.

You can run the service in two ways:

1) Using uvicorn with the ASGI entrypoint (recommended for previews)
   From the PhysicalLayerService directory:
   ```bash
   # from sda-satellite-link-216445-217124/PhysicalLayerService
   export PORT=3001   # choose from {3000,3001,3002,5000}
   uvicorn main:app --host 0.0.0.0 --port "$PORT"
   ```

2) Using Python module execution (also supported)
   ```bash
   # from sda-satellite-link-216445-217124/PhysicalLayerService
   export PORT=5000  # choose from {3000,3001,3002,5000}
   python -m src.api
   ```

Optional uvicorn flags can be configured via environment variables:

- `UVICORN_RELOAD` (true/false)
- `UVICORN_WORKERS` (integer)
- `UVICORN_LOG_LEVEL` (e.g., info, debug)

Refer to `.env.example` for defaults. You can copy `.env.example` to `.env` and adjust as needed.