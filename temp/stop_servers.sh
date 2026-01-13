#!/bin/bash

# Stop all EdTech backend servers

echo "🛑 Stopping EdTech Backend Servers..."

# Check if PID file exists
if [ -f ".server.pid" ]; then
    echo "📋 Reading PIDs from .server.pid..."
    while read pid; do
        if ps -p $pid > /dev/null 2>&1; then
            echo "   Killing process $pid..."
            kill $pid 2>/dev/null || kill -9 $pid 2>/dev/null
        fi
    done < .server.pid
    rm .server.pid
    echo "✅ Servers stopped"
else
    echo "⚠️  No PID file found, attempting to kill by port..."
    lsof -ti:8003 | xargs kill -9 2>/dev/null || true
    lsof -ti:8004 | xargs kill -9 2>/dev/null || true
    echo "✅ Ports 8003 and 8004 cleared"
fi

echo "🎉 All servers stopped"
