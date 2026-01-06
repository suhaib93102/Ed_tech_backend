#!/bin/bash
# Production Socket.IO Server Startup Script
# This script starts the Django application with Uvicorn ASGI server
# which is required for Socket.IO to work properly

cd "$(dirname "$0")"

echo "🚀 Starting Production Socket.IO Server..."
echo "========================================"
echo "Server: Uvicorn ASGI"
echo "Port: 8003"
echo "Features: Django + Socket.IO"
echo "========================================"

# Set environment variables
export DJANGO_SETTINGS_MODULE=edtech_project.settings

# Start Uvicorn with proper configuration for production
python -m uvicorn edtech_project.asgi:application \
    --host 0.0.0.0 \
    --port 8003 \
    --workers 1 \
    --loop uvloop \
    --http httptools \
    --access-log \
    --log-level info \
    --reload \
    --reload-delay 1.0

echo "Server stopped."