# Multi-stage Dockerfile for Telegram Image Enhancement Bot
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libopencv-dev \
    python3-opencv \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY pyproject.toml uv.lock* ./

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir python-telegram-bot==20.7 \
    pillow \
    opencv-python \
    numpy \
    flask \
    requests==2.32.4 \
    python-dotenv==1.1.1 \
    && pip cache purge

# Create directories
RUN mkdir -p /tmp/bot_images static/css static/js templates bot utils

# Copy application files
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash botuser && \
    chown -R botuser:botuser /app /tmp/bot_images
USER botuser

# Expose ports
EXPOSE 5000 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1
    
# Default command (can be overridden)
CMD ["python", "main.py"]
