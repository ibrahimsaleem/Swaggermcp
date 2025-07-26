# SwaggerMCP Dockerfile
# Multi-stage build for optimized production image

# Build stage
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.11-slim

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PORT=8000
ENV API_PORT=8001

# Create non-root user
RUN groupadd -r swagger && useradd -r -g swagger swagger

# Set working directory
WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /home/swagger/.local

# Copy application code
COPY core/ ./core/
COPY utils/ ./utils/
COPY examples/ ./examples/
COPY configs/ ./configs/

# Create necessary directories
RUN mkdir -p uploads cache && chown -R swagger:swagger /app

# Switch to non-root user
USER swagger

# Expose ports
EXPOSE 8000 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/status', timeout=5)" || exit 1

# Default command
CMD ["python", "core/server.py"] 