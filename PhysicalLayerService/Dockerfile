# syntax=docker/dockerfile:1
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install runtime dependencies
RUN pip install --no-cache-dir --upgrade pip

# Copy dependency files and install
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy source
COPY app /app/app
COPY .env /app/.env 2>/dev/null || true

# Expose port
ENV PORT=3000
EXPOSE 3000

# Default command - module-based startup (no venv activation required)
CMD [ "python", "-m", "app.main" ]
