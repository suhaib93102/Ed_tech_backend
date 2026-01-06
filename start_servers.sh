#!/bin/bash

# Production Server Startup Script
# Runs both Django HTTP server and Socket.IO WebSocket server

echo "🚀 Starting EdTech Backend Servers..."

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}📁 Working directory: ${SCRIPT_DIR}${NC}"

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo -e "${GREEN}✅ Virtual environment found${NC}"
    source venv/bin/activate
elif [ -d "../venv" ]; then
    echo -e "${GREEN}✅ Virtual environment found in parent directory${NC}"
    source ../venv/bin/activate
else
    echo -e "${RED}❌ Virtual environment not found${NC}"
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
fi

# Kill any existing servers on ports 8003 and 8004
echo -e "${BLUE}🔍 Checking for existing servers...${NC}"
lsof -ti:8003 | xargs kill -9 2>/dev/null || true
lsof -ti:8004 | xargs kill -9 2>/dev/null || true

echo -e "${GREEN}✅ Ports 8003 and 8004 are clear${NC}"

# Start Django HTTP server
echo -e "${BLUE}🌐 Starting Django HTTP server on port 8003...${NC}"
python manage.py runserver 8003 > logs/django.log 2>&1 &
DJANGO_PID=$!
echo -e "${GREEN}✅ Django server started (PID: $DJANGO_PID)${NC}"

# Wait a moment for Django to start
sleep 2

# Start Socket.IO server
echo -e "${BLUE}🔌 Starting Socket.IO WebSocket server on port 8004...${NC}"
python start_socketio.py > logs/socketio.log 2>&1 &
SOCKETIO_PID=$!
echo -e "${GREEN}✅ Socket.IO server started (PID: $SOCKETIO_PID)${NC}"

# Create a PID file for easy cleanup
echo "$DJANGO_PID" > .server.pid
echo "$SOCKETIO_PID" >> .server.pid

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════${NC}"
echo -e "${GREEN}🎉 All servers started successfully!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════${NC}"
echo ""
echo -e "${BLUE}📡 Django HTTP API:${NC} http://localhost:8003/api/"
echo -e "${BLUE}🔌 Socket.IO Server:${NC} http://localhost:8004"
echo ""
echo -e "${BLUE}📋 Logs:${NC}"
echo -e "   Django:    tail -f logs/django.log"
echo -e "   Socket.IO: tail -f logs/socketio.log"
echo ""
echo -e "${BLUE}🛑 To stop servers:${NC}"
echo -e "   ./stop_servers.sh"
echo -e "   or: kill $DJANGO_PID $SOCKETIO_PID"
echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════${NC}"

# Keep script running to show live logs
echo -e "${BLUE}📝 Press Ctrl+C to stop watching logs (servers will continue running)${NC}"
echo ""

# Tail both log files
tail -f logs/django.log logs/socketio.log 2>/dev/null
