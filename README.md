# Project Repository

This is the initial README file for the project.

## Running PhysicalLayerService

The PhysicalLayerService FastAPI app supports an environment variable `PORT` and binds to `0.0.0.0`. Allowed ports are: 3000, 3001, 3002, 5000. If `PORT` is not set or invalid, it defaults to `5000`.

Example:

```bash
# from sda-satellite-link-216445-217124/PhysicalLayerService
export PORT=5000  # choose from {3000,3001,3002,5000}
python -m src.api
```

You can also configure optional uvicorn flags via environment variables:

- `UVICORN_RELOAD` (true/false)
- `UVICORN_WORKERS` (integer)
- `UVICORN_LOG_LEVEL` (e.g., info, debug)

Refer to `.env.example` for defaults.