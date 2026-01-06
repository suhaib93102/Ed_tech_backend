#!/bin/bash
# Backend Deployment Script for EdTech Project
# This script builds and starts the Django backend with Socket.IO support

echo "🚀 Starting EdTech Backend Deployment..."

# Set environment variables
export DJANGO_SETTINGS_MODULE=edtech_project.settings

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Install/update dependencies
echo "📥 Installing requirements..."
pip install --upgrade pip
pip install -r requirements.txt

# Run database migrations
echo "🗄️ Running database migrations..."
python manage.py migrate

# Collect static files (for production)
echo "📂 Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser if it doesn't exist (optional)
echo "👤 Checking for admin user..."
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'admin123')" | python manage.py shell

# Start the server
echo "🌐 Starting server on port 8003..."
echo "Server will be available at: http://localhost:8003"
echo "Admin panel: http://localhost:8003/admin/"
echo "API docs: http://localhost:8003/api/docs/"
echo ""
echo "To stop the server, press Ctrl+C"
echo ""

# Start with uvicorn (production mode without --reload)
python -m uvicorn edtech_project.asgi:application --host 0.0.0.0 --port 8003 --workers 4