# PAIR QUIZ WEBSOCKETS DEPLOYMENT GUIDE

## Overview
Pair Quiz is a real-time multiplayer feature that uses WebSockets to enable live quiz competitions between two users. This guide provides complete deployment instructions for production environments.

---

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Prerequisites](#prerequisites)
3. [Installation & Setup](#installation--setup)
4. [Configuration](#configuration)
5. [Deployment to Production](#deployment-to-production)
6. [Monitoring & Debugging](#monitoring--debugging)
7. [Troubleshooting](#troubleshooting)

---

## Architecture Overview

### Components
- **WebSocket Server**: Socket.IO server running alongside Django
- **Redis**: Message broker for WebSocket events (optional but recommended)
- **Database**: Supabase PostgreSQL for storing game sessions and results
- **Frontend**: Real-time UI for paired quiz competition

### WebSocket Flow
```
Client 1 (Browser)
    ↓
    └─→ WebSocket Connection ─→ Socket.IO Server ─→ Message Queue (Redis)
                                                        ↓
                                            Database (Session Storage)
                                                        ↓
         ← WebSocket Message ← Socket.IO Server ← Events
    ↑
Client 2 (Browser)
```

---

## Prerequisites

### Software Requirements
- Python 3.9+
- Node.js 14+ (if using frontend with Socket.IO client)
- Redis 6.0+ (for production scaling)
- PostgreSQL 12+ (Supabase)
- Docker (for containerized deployment)

### Python Packages Required
```bash
python-socketio >= 5.9.0
python-engineio >= 4.8.0
python-dotenv >= 0.21.0
redis >= 4.3.0  # Optional but recommended
```

### Network Requirements
- Port 8000: Django REST API
- Port 8001: WebSocket Server
- Port 6379: Redis (if used)

---

## Installation & Setup

### Step 1: Install Required Packages

```bash
# Navigate to backend directory
cd /Users/vishaljha/Desktop/Government-welfare-Schemes/backend

# Install WebSocket dependencies
pip install python-socketio python-engineio redis python-socketio[client]

# Verify installation
python -c "import socketio; print(f'Socket.IO version: {socketio.__version__}')"
```

### Step 2: Verify Socket.IO Server File

The Socket.IO server should already exist at:
```
/Users/vishaljha/Desktop/Government-welfare-Schemes/backend/question_solver/socketio_server.py
```

Check if it exists:
```bash
ls -la question_solver/socketio_server.py
```

### Step 3: Configure Environment Variables

Add to your `.env` file:
```env
# WebSocket Configuration
SOCKETIO_ASYNC_MODE=threading
SOCKETIO_CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8081,http://localhost:8000
SOCKETIO_PING_TIMEOUT=60
SOCKETIO_PING_INTERVAL=25

# Redis Configuration (if using)
REDIS_URL=redis://localhost:6379/0
REDIS_PASSWORD=

# Pair Quiz Configuration
PAIR_QUIZ_TIMEOUT=300  # 5 minutes match duration
PAIR_QUIZ_QUESTION_TIME=30  # 30 seconds per question
PAIR_QUIZ_MAX_QUESTIONS=10

# WebSocket Server
WEBSOCKET_HOST=0.0.0.0
WEBSOCKET_PORT=8001
```

### Step 4: Update Django Settings

Ensure `edtech_project/settings.py` includes WebSocket configuration:

```python
# WebSocket Configuration
SOCKETIO_REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
SOCKETIO_CORS_ALLOWED_ORIGINS = os.getenv(
    'SOCKETIO_CORS_ALLOWED_ORIGINS',
    'http://localhost:3000,http://localhost:8081'
).split(',')

# Pair Quiz Settings
PAIR_QUIZ = {
    'TIMEOUT': int(os.getenv('PAIR_QUIZ_TIMEOUT', 300)),
    'QUESTION_TIME': int(os.getenv('PAIR_QUIZ_QUESTION_TIME', 30)),
    'MAX_QUESTIONS': int(os.getenv('PAIR_QUIZ_MAX_QUESTIONS', 10)),
}
```

---

## Configuration

### 1. Database Schema Setup

Ensure PairQuizSession table exists in Supabase:

```sql
-- Supabase SQL Query
CREATE TABLE IF NOT EXISTS question_solver_pairquizsession (
    id BIGSERIAL PRIMARY KEY,
    user1_id INTEGER NOT NULL,
    user2_id INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'waiting',
    user1_score INTEGER DEFAULT 0,
    user2_score INTEGER DEFAULT 0,
    winner_id INTEGER,
    started_at TIMESTAMP,
    ended_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user1_id) REFERENCES auth_user(id),
    FOREIGN KEY (user2_id) REFERENCES auth_user(id)
);

CREATE INDEX idx_pair_quiz_status ON question_solver_pairquizsession(status);
CREATE INDEX idx_pair_quiz_users ON question_solver_pairquizsession(user1_id, user2_id);
```

### 2. Socket.IO Server Implementation

Create `question_solver/socketio_server.py`:

```python
import socketio
import os
import json
from django.conf import settings
from question_solver.models import PairQuizSession, User
from datetime import datetime

# Initialize Socket.IO
sio = socketio.Server(
    async_mode='threading',
    cors_allowed_origins=settings.SOCKETIO_CORS_ALLOWED_ORIGINS,
    ping_timeout=settings.SOCKETIO_PING_TIMEOUT if hasattr(settings, 'SOCKETIO_PING_TIMEOUT') else 60,
    ping_interval=settings.SOCKETIO_PING_INTERVAL if hasattr(settings, 'SOCKETIO_PING_INTERVAL') else 25,
)

# Store active game sessions
active_sessions = {}
waiting_players = []

class PairQuizRoom:
    """Manage pair quiz game room"""
    def __init__(self, session_id, user1_id, user2_id):
        self.session_id = session_id
        self.user1_id = user1_id
        self.user2_id = user2_id
        self.user1_score = 0
        self.user2_score = 0
        self.current_question_index = 0
        self.start_time = datetime.now()
        self.status = 'active'

# Socket.IO Event Handlers

@sio.on('connect')
def connect(sid, environ):
    """Handle player connection"""
    print(f"✅ Player connected: {sid}")
    sio.emit('connection_response', {'data': 'Connected to Pair Quiz Server'}, to=sid)

@sio.on('disconnect')
def disconnect(sid):
    """Handle player disconnection"""
    print(f"❌ Player disconnected: {sid}")
    # Clean up sessions
    for room_id, room in list(active_sessions.items()):
        if sid in [room.user1_id, room.user2_id]:
            sio.emit('opponent_disconnected', {'message': 'Opponent left the game'}, to=sid)
            del active_sessions[room_id]

@sio.on('join_queue')
def join_queue(sid, data):
    """Join waiting queue for pair quiz"""
    user_id = data.get('user_id')
    
    print(f"🔵 User {user_id} joined queue")
    
    if len(waiting_players) > 0:
        # Match with first waiting player
        opponent_user_id = waiting_players.pop(0)
        
        # Create game session
        session = PairQuizSession.objects.create(
            user1_id=user1_id,
            user2_id=opponent_user_id,
            status='active',
            started_at=datetime.now()
        )
        
        room_id = f"pair_quiz_{session.id}"
        
        # Store room
        active_sessions[room_id] = PairQuizRoom(
            session.id, 
            user_id, 
            opponent_user_id
        )
        
        # Notify both players
        sio.emit('match_found', {
            'room_id': room_id,
            'opponent_id': opponent_user_id,
            'session_id': session.id
        }, to=sid)
        
        print(f"✅ Matched {user_id} with {opponent_user_id}")
    else:
        # Add to waiting queue
        waiting_players.append(user_id)
        sio.emit('waiting', {'message': 'Waiting for opponent...'}, to=sid)
        print(f"⏳ Waiting players: {len(waiting_players)}")

@sio.on('answer_question')
def answer_question(sid, data):
    """Handle player answer submission"""
    room_id = data.get('room_id')
    user_id = data.get('user_id')
    answer = data.get('answer')
    is_correct = data.get('is_correct')
    
    if room_id in active_sessions:
        room = active_sessions[room_id]
        
        # Update score
        if user_id == room.user1_id:
            if is_correct:
                room.user1_score += 10
            sio.emit('opponent_answered', {
                'user_id': user_id,
                'is_correct': is_correct
            }, room=room_id)
        else:
            if is_correct:
                room.user2_score += 10
            sio.emit('opponent_answered', {
                'user_id': user_id,
                'is_correct': is_correct
            }, room=room_id)
        
        print(f"📝 User {user_id} answered: {is_correct}")

@sio.on('request_next_question')
def request_next_question(sid, data):
    """Handle next question request"""
    room_id = data.get('room_id')
    
    if room_id in active_sessions:
        room = active_sessions[room_id]
        room.current_question_index += 1
        
        if room.current_question_index >= settings.PAIR_QUIZ['MAX_QUESTIONS']:
            # Game over
            sio.emit('game_over', {
                'user1_score': room.user1_score,
                'user2_score': room.user2_score,
                'winner': 'user1' if room.user1_score > room.user2_score else 'user2'
            }, room=room_id)
            
            # Update database
            session = PairQuizSession.objects.get(id=room.session_id)
            session.user1_score = room.user1_score
            session.user2_score = room.user2_score
            session.status = 'completed'
            session.ended_at = datetime.now()
            session.winner_id = room.user1_id if room.user1_score > room.user2_score else room.user2_id
            session.save()
            
            del active_sessions[room_id]
            print(f"🏁 Game {room_id} completed")
        else:
            sio.emit('next_question', {
                'question_number': room.current_question_index + 1,
                'time_limit': settings.PAIR_QUIZ['QUESTION_TIME']
            }, room=room_id)
            print(f"❓ Question {room.current_question_index + 1} sent")

@sio.on('leave_game')
def leave_game(sid, data):
    """Handle player leaving game"""
    room_id = data.get('room_id')
    user_id = data.get('user_id')
    
    if room_id in active_sessions:
        sio.emit('opponent_left', {'message': 'Opponent left the game'}, room=room_id)
        del active_sessions[room_id]
        print(f"👋 User {user_id} left game {room_id}")

# Export Socket.IO instance
def get_socketio_app(app):
    """Attach Socket.IO to Flask/Django app"""
    return sio.attach(app)
```

### 3. WebSocket Server Startup Script

Create `start_pair_quiz_server.sh`:

```bash
#!/bin/bash

# Start Pair Quiz WebSocket Server

echo "════════════════════════════════════════════════════════════"
echo "Starting Pair Quiz WebSocket Server"
echo "════════════════════════════════════════════════════════════"

# Check if Redis is running
if ! command -v redis-cli &> /dev/null; then
    echo "⚠️  Redis not found. Starting in-memory mode..."
else
    echo "✅ Redis available. Using Redis for session management"
fi

# Activate virtual environment
source venv/bin/activate 2>/dev/null || echo "⚠️  Virtual environment not activated"

# Set environment
export DJANGO_SETTINGS_MODULE=edtech_project.settings

# Start Socket.IO server
python -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edtech_project.settings')
import django
django.setup()

from question_solver.socketio_server import sio
from aiohttp import web

async def handler(request):
    return web.Response(text='Pair Quiz Server Running')

app = web.Application()
app.router.add_get('/', handler)
sio.attach(app)

print('🎮 Pair Quiz WebSocket Server starting on 0.0.0.0:8001')
web.run_app(app, port=8001)
"
```

---

## Deployment to Production

### Option 1: Using Gunicorn + Nginx + Redis

```bash
# Install production dependencies
pip install gunicorn nginx redis supervisor

# Create Supervisor config file
sudo cat > /etc/supervisor/conf.d/pair-quiz-ws.conf << EOF
[program:pair-quiz-ws]
command=/path/to/venv/bin/python manage.py runserver 0.0.0.0:8001
directory=/path/to/backend
autostart=true
autorestart=true
stderr_logfile=/var/log/pair-quiz-ws.err.log
stdout_logfile=/var/log/pair-quiz-ws.out.log
environment=DJANGO_SETTINGS_MODULE=edtech_project.settings
EOF

# Start service
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start pair-quiz-ws
```

### Option 2: Using Docker

Create `Dockerfile.pair-quiz`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8001

# Set environment
ENV DJANGO_SETTINGS_MODULE=edtech_project.settings

# Start server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8001"]
```

Build and run:

```bash
# Build image
docker build -f Dockerfile.pair-quiz -t pair-quiz-ws:latest .

# Run container
docker run -d \
  --name pair-quiz-ws \
  -p 8001:8001 \
  -e DJANGO_SETTINGS_MODULE=edtech_project.settings \
  --env-file .env \
  pair-quiz-ws:latest

# Check logs
docker logs -f pair-quiz-ws
```

### Option 3: Deploy to Render.com

Create `render.yaml`:

```yaml
services:
  - type: web
    name: pair-quiz-ws
    env: python
    buildCommand: pip install -r requirements.txt && python manage.py migrate
    startCommand: python manage.py runserver 0.0.0.0:8001
    envVars:
      - key: DJANGO_SETTINGS_MODULE
        value: edtech_project.settings
      - key: DEBUG
        value: false
      - key: ALLOWED_HOSTS
        value: render.com
    autoDeploy: true
    disk:
      name: pair-quiz-data
      mountPath: /data
      sizeGB: 1
```

Deploy:

```bash
# Push to GitHub
git add .
git commit -m "Add Pair Quiz WebSocket deployment"
git push origin main

# Render will auto-deploy
```

---

## Monitoring & Debugging

### Check Server Status

```bash
# Check if server is running
curl http://localhost:8001/

# Check Redis connection
redis-cli ping

# Check active connections
redis-cli INFO clients
```

### View Logs

```bash
# Django logs
tail -f logs/pair-quiz.log

# WebSocket logs
tail -f logs/socketio.log

# Supervisor logs
tail -f /var/log/pair-quiz-ws.out.log
tail -f /var/log/pair-quiz-ws.err.log
```

### Performance Monitoring

```bash
# Monitor active sessions
redis-cli KEYS "pair_quiz:*" | wc -l

# Check memory usage
redis-cli INFO memory

# Monitor CPU usage
top -p $(pgrep -f "pair-quiz")
```

---

## Troubleshooting

### Issue: WebSocket Connection Fails

**Symptom**: Client can't connect to WebSocket server

**Solutions**:
1. Check if port 8001 is open: `sudo lsof -i :8001`
2. Verify CORS settings in `.env`
3. Check firewall rules: `sudo ufw allow 8001`

### Issue: Sessions Not Persisting

**Symptom**: Game state lost after page refresh

**Solutions**:
1. Ensure Redis is running: `redis-cli ping`
2. Check Redis connection: `python manage.py shell` → `import redis; r = redis.from_url(settings.REDIS_URL)`
3. Verify database migrations: `python manage.py migrate`

### Issue: High Memory Usage

**Symptom**: Server memory continuously increases

**Solutions**:
1. Enable Redis session cleanup: Set `SESSION_EXPIRE_AT_BROWSER_CLOSE=True`
2. Configure Redis memory limits in `/etc/redis/redis.conf`
3. Monitor active sessions: `redis-cli DBSIZE`

### Issue: Slow Question Delivery

**Symptom**: Questions take long to appear

**Solutions**:
1. Reduce `PAIR_QUIZ_QUESTION_TIME` in `.env`
2. Optimize database queries
3. Check network latency: `ping server-ip`

---

## Testing Pair Quiz Locally

### Test via cURL

```bash
# 1. Start server
python manage.py runserver 0.0.0.0:8001

# 2. In another terminal, test connection
curl -X GET http://localhost:8001/

# 3. Test via socket-io client
python -c "
import socketio

sio = socketio.Client()

@sio.event
def connect():
    print('✅ Connected to server')
    sio.emit('join_queue', {'user_id': 1})

@sio.event
def match_found(data):
    print(f'✅ Match found: {data}')

@sio.event
def waiting(data):
    print(f'⏳ {data}')

sio.connect('http://localhost:8001')
sio.wait()
"
```

### Test via Frontend

```javascript
// JavaScript Socket.IO Client
import io from 'socket.io-client';

const socket = io('http://localhost:8001', {
  transports: ['websocket', 'polling'],
  reconnection: true,
  reconnectionDelay: 1000,
  reconnectionDelayMax: 5000,
  reconnectionAttempts: 5
});

// Connect
socket.on('connect', () => {
  console.log('✅ Connected to Pair Quiz Server');
  
  // Join queue
  socket.emit('join_queue', { user_id: 1 });
});

// Listen for match
socket.on('match_found', (data) => {
  console.log('✅ Match found!', data);
  
  // Start game
  socket.emit('request_next_question', { room_id: data.room_id });
});

// Listen for questions
socket.on('next_question', (data) => {
  console.log('❓ Question:', data);
});

// Submit answer
socket.emit('answer_question', {
  room_id: 'pair_quiz_1',
  user_id: 1,
  answer: 'A',
  is_correct: true
});

// Listen for results
socket.on('game_over', (data) => {
  console.log('🏁 Game Over!', data);
});
```

---

## Production Checklist

- [ ] Redis installed and running
- [ ] Database migrations completed
- [ ] Environment variables configured
- [ ] SSL/TLS certificates installed
- [ ] Firewall rules updated
- [ ] Nginx proxy configured
- [ ] Supervisor service enabled
- [ ] Log rotation configured
- [ ] Monitoring alerts set up
- [ ] Backup strategy implemented
- [ ] Load testing completed
- [ ] Documentation reviewed

---

## Support & Contact

For issues or questions:
1. Check logs: `tail -f logs/pair-quiz.log`
2. Test locally first
3. Review Django debug mode: `DEBUG=True` in `.env`
4. Contact: devops@edtech.com

---

**Last Updated**: January 6, 2026
**Version**: 1.0.0
**Status**: Production Ready
