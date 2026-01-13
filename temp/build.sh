#!/bin/bash
# Render Build Script for EdTech Backend
# This script handles the build process for Render deployment

echo "🚀 Starting Render Build Process..."

# Set Python path
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Upgrade pip
pip install --upgrade pip

# Install system dependencies for Pillow (if needed)
# Note: Render should have these, but just in case
apt-get update && apt-get install -y \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    libtiff-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libwebp-dev \
    tcl8.6-dev \
    tk8.6-dev \
    python3-tk \
    || true

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --no-cache-dir -r requirements.txt

# Run Django migrations
echo "🗄️ Running database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "📂 Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser if needed (for development)
echo "👤 Setting up admin user..."
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'admin123')" | python manage.py shell

echo "✅ Build completed successfully!"