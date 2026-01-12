# Multi-stage build for Ed-Tech backend
FROM python:3.12-slim

# Install system dependencies for OCR and PDF processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Tesseract OCR - core OCR engine
    tesseract-ocr \
    libtesseract-dev \
    \
    # Image processing support
    libjpeg-dev \
    libpng-dev \
    libwebp-dev \
    libtiff-dev \
    libopenjp2-7 \
    \
    # PDF processing
    poppler-utils \
    libpoppler-cpp-dev \
    \
    # Build tools
    build-essential \
    gcc \
    g++ \
    pkg-config \
    \
    # Database client
    postgresql-client \
    \
    # Cleanup
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create directories for static files and media
RUN mkdir -p /app/staticfiles /app/media /app/logs

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000

# Run migrations and collect static files
RUN python manage.py collectstatic --noinput --clear 2>/dev/null || true

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:$PORT/api/health/').read()" || exit 1

# Start application
CMD ["gunicorn", \
     "edtech_project.wsgi:application", \
     "--workers=2", \
     "--worker-class=sync", \
     "--bind=0.0.0.0:$PORT", \
     "--timeout=120", \
     "--access-logfile=-", \
     "--error-logfile=-"]
