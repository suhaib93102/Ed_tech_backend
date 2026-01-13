# Pair Quiz WebSocket Deployment Guide

## Overview
This guide provides step-by-step instructions to deploy the Pair Quiz feature with WebSocket support for real-time multiplayer gameplay.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      Frontend (React)                            │
│  (WebSocket Client for Real-time Updates)                       │
└─────────────┬───────────────────────────────────────────────────┘
              │
              │ WebSocket Connection (ws://)
              │
┌─────────────v───────────────────────────────────────────────────┐
│                   Django + Socket.IO Server                      │
│  (Handles multiple pair quiz sessions concurrently)             │
└─────────────┬───────────────────────────────────────────────────┘
              │
              │ Database Queries
              │
┌─────────────v───────────────────────────────────────────────────┐
│              Supabase PostgreSQL Database                        │
│  (Stores pair quiz sessions, user data, feature usage logs)     │
└─────────────────────────────────────────────────────────────────┘
```

## Prerequisites

- Django 5.0.0
- Python 3.10+
- Supabase PostgreSQL connection configured
- python-socketio library
- python-engineio library
- Redis (optional, for session caching)

## Step 1: Install Required Dependencies

```bash
# Navigate to backend directory
cd /Users/vishaljha/Desktop/Government-welfare-Schemes/backend

# Install Socket.IO packages
pip install python-socketio[client] python-engineio
pip install aiohttp  # For async WebSocket support
pip install redis    # For session management (optional)
```

### Check current dependencies:
```bash
pip list | grep -i socket
pip list | grep -i engineio
```

## Step 2: Configure Socket.IO Server

### Create/Update `socketio_server.py`

```python
# File: question_solver/socketio_server.py

import socketio
from datetime import datetime
import json
import os

# Initialize Socket.IO server
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins='*',
    ping_timeout=60,
    ping_interval=25,
    logger=True,
    engineio_logger=True
)

# Store active sessions
active_sessions = {}
active_players = {}

@sio.on('connect')
async def connect(sid, environ):
    """Handle new WebSocket connection"""
    print(f'Client connected: {sid}')

@sio.on('disconnect')
async def disconnect(sid):
    """Handle client disconnection"""
    print(f'Client disconnected: {sid}')
    
    # Clean up session if user was in a pair quiz
    if sid in active_players:
        session_id = active_players[sid]
        if session_id in active_sessions:
            # Notify other player
            other_player = active_sessions[session_id]['players'].get('player2')
            if other_player and other_player != sid:
                await sio.emit('opponent_disconnected', 
                              {'session_id': session_id},
                              to=other_player)
            del active_sessions[session_id]
        del active_players[sid]

@sio.on('create_pair_quiz')
async def create_pair_quiz(sid, data):
    """Handle pair quiz creation request"""
    from question_solver.models import PairQuizSession
    from django.utils import timezone
    import uuid
    
    try:
        user_id = data.get('user_id')
        topic = data.get('topic', 'General')
        
        # Create new session
        session_id = str(uuid.uuid4())
        
        session = PairQuizSession.objects.create(
            session_id=session_id,
            user1_id=user_id,
            topic=topic,
            started_at=timezone.now(),
            status='waiting'
        )
        
        # Store in memory
        active_sessions[session_id] = {
            'session_id': session_id,
            'topic': topic,
            'players': {'player1': sid},
            'created_at': timezone.now(),
            'status': 'waiting'
        }
        
        active_players[sid] = session_id
        
        # Emit success
        await sio.emit('quiz_created', {
            'session_id': session_id,
            'topic': topic,
            'join_url': f'/pair-quiz/{session_id}',
            'status': 'waiting_for_opponent'
        }, to=sid)
        
        print(f'Pair quiz session created: {session_id}')
        
    except Exception as e:
        await sio.emit('error', {'message': str(e)}, to=sid)

@sio.on('join_pair_quiz')
async def join_pair_quiz(sid, data):
    """Handle user joining existing pair quiz"""
    session_id = data.get('session_id')
    user_id = data.get('user_id')
    
    if session_id not in active_sessions:
        await sio.emit('error', {'message': 'Session not found'}, to=sid)
        return
    
    session = active_sessions[session_id]
    
    if 'player2' in session['players']:
        await sio.emit('error', {'message': 'Session is full'}, to=sid)
        return
    
    # Add second player
    session['players']['player2'] = sid
    session['status'] = 'ready'
    active_players[sid] = session_id
    
    # Notify both players
    await sio.emit('opponent_joined', {
        'session_id': session_id,
        'status': 'ready_to_start'
    }, to=session['players']['player1'])
    
    await sio.emit('opponent_joined', {
        'session_id': session_id,
        'status': 'ready_to_start'
    }, to=sid)
    
    print(f'Player 2 joined session: {session_id}')

@sio.on('start_quiz')
async def start_quiz(sid, data):
    """Start the pair quiz for both players"""
    session_id = data.get('session_id')
    
    if session_id not in active_sessions:
        await sio.emit('error', {'message': 'Session not found'}, to=sid)
        return
    
    session = active_sessions[session_id]
    session['status'] = 'in_progress'
    session['started_at'] = datetime.now()
    
    # Get quiz questions
    from question_solver.models import Question
    
    questions = list(
        Question.objects.filter(
            topic=session['topic']
        )[:5]  # Get 5 questions
    )
    
    # Send same questions to both players
    for player_sid in session['players'].values():
        await sio.emit('quiz_started', {
            'session_id': session_id,
            'questions': [
                {
                    'id': q.id,
                    'text': q.text,
                    'options': [q.option_a, q.option_b, q.option_c, q.option_d]
                } for q in questions
            ],
            'time_limit': 30
        }, to=player_sid)
    
    print(f'Quiz started for session: {session_id}')

@sio.on('submit_answer')
async def submit_answer(sid, data):
    """Handle answer submission"""
    session_id = data.get('session_id')
    question_id = data.get('question_id')
    answer = data.get('answer')
    
    if session_id not in active_sessions:
        return
    
    session = active_sessions[session_id]
    
    # Store answer
    if 'answers' not in session:
        session['answers'] = {}
    
    session['answers'][question_id] = {
        'player': sid,
        'answer': answer,
        'timestamp': datetime.now().isoformat()
    }
    
    # Notify players of answer submission
    await sio.emit('answer_submitted', {
        'question_id': question_id,
        'player': 'you' if sid == active_players.get(sid) else 'opponent'
    }, to=sid)
    
    print(f'Answer submitted for question {question_id} in session {session_id}')

@sio.on('quiz_completed')
async def quiz_completed(sid, data):
    """Handle quiz completion"""
    session_id = data.get('session_id')
    score = data.get('score')
    
    if session_id not in active_sessions:
        return
    
    session = active_sessions[session_id]
    session['status'] = 'completed'
    
    if 'results' not in session:
        session['results'] = {}
    
    session['results'][sid] = {
        'score': score,
        'completed_at': datetime.now().isoformat()
    }
    
    # If both players completed, show results
    if len(session['results']) == 2:
        # Emit results to both players
        for player_sid, result in session['results'].items():
            await sio.emit('quiz_results', {
                'your_score': result['score'],
                'session_id': session_id
            }, to=player_sid)
    
    print(f'Quiz completed for session {session_id}')

# WebSocket Middleware for Django
class SocketIOMiddleware:
    """Middleware to attach Socket.IO app to Django"""
    def __init__(self, asgi_app):
        self.asgi_app = asgi_app
        self.socketio_app = socketio.ASGIApp(sio, self.asgi_app)
    
    async def __call__(self, scope, receive, send):
        if scope['type'] == 'websocket':
            await self.socketio_app(scope, receive, send)
        else:
            await self.asgi_app(scope, receive, send)
```

## Step 3: Configure ASGI (Async Server Gateway Interface)

### Update `asgi.py`

```python
# File: edtech_project/asgi.py

import os
from django.core.asgi import get_asgi_application
from question_solver.socketio_server import SocketIOMiddleware

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edtech_project.settings')

# Get Django ASGI app
django_asgi_app = get_asgi_application()

# Add Socket.IO middleware
application = SocketIOMiddleware(django_asgi_app)
```

## Step 4: Update WSGI Configuration

### Add Socket.IO support to `wsgi.py`

```python
# File: edtech_project/wsgi.py

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edtech_project.settings')

application = get_wsgi_application()

# For development with Socket.IO
try:
    from daphne.cli import CommandLineInterface
    # This enables ASGI support
except ImportError:
    pass
```

## Step 5: Update Django Settings

### Add to `settings.py`

```python
# File: edtech_project/settings.py

# ... existing settings ...

# WebSocket Configuration
INSTALLED_APPS = [
    # ... existing apps ...
    'socketio',  # Add if using django-socketio
]

# ASGI Configuration
ASGI_APPLICATION = 'edtech_project.asgi.application'

# WebSocket Settings
WEBSOCKET_ACCEPT_ALL = True
WEBSOCKET_URL = '/ws/'

# Allow all origins for WebSocket (customize for production)
WEBSOCKET_ALLOWED_ORIGINS = [
    'http://localhost:8081',
    'http://localhost:3000',
    'http://127.0.0.1:8081',
    'http://127.0.0.1:3000',
    'https://yourdomain.com',  # Production domain
]

# Socket.IO Configuration
SOCKETIO_OPTIONS = {
    'ping_timeout': 60,
    'ping_interval': 25,
    'logger': True,
    'engineio_logger': True,
}
```

## Step 6: Install Web Server for Async Support

```bash
# Install Daphne for ASGI support (production)
pip install daphne

# Or use Uvicorn for lighter deployment
pip install uvicorn

# For development use Django's development server with async support
pip install channels  # Alternative for WebSocket support
```

## Step 7: Update URL Configuration

### Add Socket.IO routes to `urls.py`

```python
# File: edtech_project/urls.py

from django.contrib import admin
from django.urls import path, include, re_path
from question_solver.socketio_server import sio
from django.views.static import serve
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('question_solver.urls')),
    
    # Socket.IO endpoint
    re_path(r'^ws/$', sio.handler),
    
    # Static and Media files
    path('static/<path:path>', serve, {'document_root': settings.STATIC_ROOT}),
    path('media/<path:path>', serve, {'document_root': settings.MEDIA_ROOT}),
]

if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

## Step 8: Create Frontend WebSocket Client

### Example React Component

```javascript
// File: frontend/src/components/PairQuiz.jsx

import React, { useState, useEffect } from 'react';
import io from 'socket.io-client';

const PairQuiz = () => {
  const [socket, setSocket] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const [status, setStatus] = useState('idle');
  const [topic, setTopic] = useState('General');

  useEffect(() => {
    // Connect to Socket.IO server
    const newSocket = io('http://localhost:8000', {
      transports: ['websocket', 'polling'],
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000,
      reconnectionAttempts: 5,
    });

    newSocket.on('connect', () => {
      console.log('Connected to pair quiz server');
    });

    newSocket.on('quiz_created', (data) => {
      setSessionId(data.session_id);
      setStatus('waiting');
    });

    newSocket.on('opponent_joined', (data) => {
      setStatus('ready');
    });

    newSocket.on('quiz_started', (data) => {
      setStatus('in_progress');
      // Display questions
    });

    newSocket.on('quiz_results', (data) => {
      setStatus('completed');
      // Display results
    });

    newSocket.on('opponent_disconnected', () => {
      setStatus('opponent_left');
    });

    newSocket.on('error', (data) => {
      console.error('Error:', data.message);
    });

    setSocket(newSocket);

    return () => {
      newSocket.disconnect();
    };
  }, []);

  const createQuiz = () => {
    socket.emit('create_pair_quiz', {
      user_id: 1,  // Replace with actual user ID
      topic: topic,
    });
  };

  const joinQuiz = () => {
    socket.emit('join_pair_quiz', {
      session_id: sessionId,
      user_id: 1,  // Replace with actual user ID
    });
  };

  const startQuiz = () => {
    socket.emit('start_quiz', {
      session_id: sessionId,
    });
  };

  return (
    <div className="pair-quiz">
      <h2>Pair Quiz</h2>
      <p>Status: {status}</p>
      
      {status === 'idle' && (
        <>
          <input 
            value={topic} 
            onChange={(e) => setTopic(e.target.value)}
            placeholder="Enter topic"
          />
          <button onClick={createQuiz}>Create Quiz</button>
        </>
      )}
      
      {status === 'waiting' && (
        <>
          <p>Session ID: {sessionId}</p>
          <p>Waiting for opponent...</p>
        </>
      )}
      
      {status === 'ready' && (
        <>
          <p>Opponent joined! Ready to start.</p>
          <button onClick={startQuiz}>Start Quiz</button>
        </>
      )}
    </div>
  );
};

export default PairQuiz;
```

## Step 9: Run the Server

### Development Mode

```bash
# Option 1: Using Daphne (recommended for development with WebSocket)
daphne -b 0.0.0.0 -p 8000 edtech_project.asgi:application

# Option 2: Using Uvicorn (lightweight)
uvicorn edtech_project.asgi:application --host 0.0.0.0 --port 8000 --reload

# Option 3: Using Gunicorn with Daphne worker (production-like)
gunicorn edtech_project.wsgi:application -k daphne.workers.UvicornWorker -b 0.0.0.0:8000
```

### Development with Django's Built-in Server

```bash
# Note: Django's development server doesn't support WebSocket natively
# Use one of the options above for WebSocket functionality
python manage.py runserver 0.0.0.0:8000
```

## Step 10: Deploy to Production

### Option 1: Render.com

```yaml
# File: render.yaml

services:
  - type: web
    name: edtech-api
    runtime: python
    buildCommand: |
      pip install -r requirements.txt
      python manage.py migrate
    startCommand: daphne -b 0.0.0.0 -p $PORT edtech_project.asgi:application
    envVars:
      - key: DJANGO_SETTINGS_MODULE
        value: edtech_project.settings
      - key: DEBUG
        value: "False"
      - key: SUPABASE_URL
        sync: false
      - key: JWT_SECRET
        sync: false
```

### Option 2: Docker

```dockerfile
# File: Dockerfile

FROM python:3.10

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN pip install daphne gunicorn

# Copy project
COPY . .

# Create static files
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Run with Daphne for WebSocket support
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "edtech_project.asgi:application"]
```

```yaml
# File: docker-compose.yml

version: '3.9'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      DEBUG: "False"
      SUPABASE_URL: ${SUPABASE_URL}
      JWT_SECRET: ${JWT_SECRET}
    depends_on:
      - db
  
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: edtech
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### Option 3: Heroku (with WebSocket support)

```bash
# Add WebSocket buildpack
heroku buildpacks:add heroku-community/apt
heroku buildpacks:add heroku/python

# Create Procfile
echo "web: daphne -b 0.0.0.0 -p \$PORT edtech_project.asgi:application" > Procfile

# Deploy
git push heroku main
```

## Step 11: Testing

### Test WebSocket Connection

```bash
# Install websocat for testing
brew install websocat  # macOS

# Connect to WebSocket
websocat ws://localhost:8000/ws/
```

### Test with curl (REST endpoints)

```bash
# Create pair quiz session
curl -X POST http://localhost:8000/api/pair-quiz/create/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"topic": "General"}'

# Join pair quiz session
curl -X POST http://localhost:8000/api/pair-quiz/join/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"session_id": "YOUR_SESSION_ID"}'
```

## Troubleshooting

### WebSocket Connection Failed
- **Problem**: "WebSocket connection refused"
- **Solution**: Ensure Daphne or Uvicorn is running, not Django's dev server
  ```bash
  ps aux | grep daphne
  ```

### CORS Issues
- **Problem**: "Cross-Origin Request Blocked"
- **Solution**: Update WEBSOCKET_ALLOWED_ORIGINS in settings.py with frontend URL

### Session Not Found
- **Problem**: "Session ID not found"
- **Solution**: Check if session ID is correct and session hasn't expired

### Database Connection Issues
- **Problem**: "Supabase connection refused"
- **Solution**: Verify SUPABASE_URL and network connectivity
  ```bash
  psql -c "select 1" -d $SUPABASE_URL
  ```

## Monitoring

### Monitor WebSocket Connections

```python
# Add to settings.py
SOCKETIO_OPTIONS = {
    'logger': True,
    'engineio_logger': True,
}

# View logs
tail -f /var/log/daphne.log
```

### Monitor Database Connections

```sql
-- Check active connections
SELECT datname, count(*) 
FROM pg_stat_activity 
GROUP BY datname;

-- Check long-running queries
SELECT * FROM pg_stat_activity 
WHERE state = 'active' 
ORDER BY query_start DESC;
```

## Performance Optimization

1. **Enable connection pooling**
   ```python
   # Add to settings.py
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'CONN_MAX_AGE': 600,
           'OPTIONS': {
               'connect_timeout': 10,
           }
       }
   }
   ```

2. **Use Redis for session caching**
   ```bash
   pip install redis django-redis
   ```

3. **Enable gzip compression**
   ```python
   MIDDLEWARE = [
       'django.middleware.gzip.GZipMiddleware',
       # ... other middleware
   ]
   ```

## Summary

Pair Quiz WebSocket deployment is complete! You can now:

✅ Create multiplayer quiz sessions in real-time
✅ Support simultaneous connections for multiple player pairs
✅ Sync questions and answers across both players
✅ Display live results as players complete

**Next Steps:**
1. Test locally with Daphne
2. Deploy to staging environment
3. Configure production domain and SSL
4. Set up monitoring and alerts
5. Load test with multiple concurrent sessions
