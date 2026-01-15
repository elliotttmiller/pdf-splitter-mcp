# Stage 1: Build (Uses uv for speed)
FROM python:3.11-slim-bookworm as builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app
COPY pyproject.toml .

# Install dependencies to a virtual env
RUN uv venv /app/.venv && \
    uv pip install -r pyproject.toml

# Stage 2: Runtime (Small & Secure)
FROM python:3.11-slim-bookworm

WORKDIR /app

# Install curl for healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# Copy virtual env
COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Copy App Code
COPY ./app ./app

# Create Non-Root User
RUN groupadd -g 1000 appuser && \
    useradd -u 1000 -g appuser appuser && \
    mkdir -p /data/temp && \
    chown -R appuser:appuser /data

USER appuser

# Config
ENV PYTHONPATH=/app \
    MCP_HOST=0.0.0.0 \
    MCP_PORT=8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
