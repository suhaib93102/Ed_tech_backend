#!/bin/bash
# Production Server Startup Script with Socket.IO Support

echo "🚀 Starting EdTech Backend with Socket.IO Support"
echo "=================================================="

# Kill any existing processes on port 8003
echo "🔍 Checking for existing processes on port 8003..."
if lsof -ti:8003 > /dev/null 2>&1; then
    echo "   Killing existing processes..."
    lsof -ti:8003 | xargs kill -9 2>/dev/null
    sleep 2
fi

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "🔧 Activating virtual environment..."
    source venv/bin/activate
fi

# Install required packages
echo "📦 Checking dependencies..."
pip install -q uvicorn python-socketio aiohttp

# Run with Uvicorn for ASGI support (required for Socket.IO)
echo ""
echo "✅ Starting server with Uvicorn (ASGI + Socket.IO)..."
echo "   URL: http://localhost:8003"
echo "   Socket.IO: ws://localhost:8003/socket.io/"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=================================================="
echo ""

uvicorn edtech_project.asgi:application \
    --host 0.0.0.0 \
    --port 8003 \
    --reload \
    --log-level info
