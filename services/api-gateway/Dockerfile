# DevOps Multi-Agent Ecosystem - API Gateway
# Production-ready multi-stage Dockerfile

# Build stage
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# Production stage
FROM python:3.11-slim

# Security: Create non-root user
RUN groupadd --gid 1000 appgroup && \
    useradd --uid 1000 --gid appgroup --shell /bin/bash --create-home appuser

WORKDIR /app

# Install runtime dependencies only
COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache-dir /wheels/* && rm -rf /wheels

# Copy application code
COPY --chown=appuser:appgroup app.py .

# Security: Switch to non-root user
USER appuser

# Environment configuration
ENV PORT=8080
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')" || exit 1

# Run application
CMD ["python", "app.py"]

# Labels for metadata
LABEL org.opencontainers.image.title="DevOps Multi-Agent API Gateway"
LABEL org.opencontainers.image.description="API Gateway for the DevOps Multi-Agent Ecosystem"
LABEL org.opencontainers.image.version="1.0.0"
LABEL org.opencontainers.image.authors="devops-team"
LABEL org.opencontainers.image.source="https://github.com/devops-multiagents"
