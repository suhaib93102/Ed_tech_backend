#!/usr/bin/env python3
"""
Socket.IO WebSocket Server Starter
Production-ready standalone server for real-time features
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Add backend directory to Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edtech_project.settings')
import django
django.setup()

from question_solver.socketio_server import sio
import uvicorn
from django.conf import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def create_socketio_app():
    """Create Socket.IO ASGI application"""
    from socketio import ASGIApp
    
    # Wrap Socket.IO server in ASGI app
    app = ASGIApp(
        sio,
        other_asgi_app=None,  # No other ASGI app needed
        socketio_path='socket.io'
    )
    
    return app

def main():
    """Main entry point"""
    logger.info("=" * 80)
    logger.info("🚀 Starting Socket.IO WebSocket Server")
    logger.info("=" * 80)
    
    # Get configuration
    host = os.getenv('SOCKETIO_HOST', '0.0.0.0')
    port = int(os.getenv('SOCKETIO_PORT', 8004))
    
    logger.info(f"📡 Server Configuration:")
    logger.info(f"   Host: {host}")
    logger.info(f"   Port: {port}")
    logger.info(f"   Socket.IO Path: /socket.io/")
    logger.info(f"   Transports: polling, websocket")
    logger.info(f"   CORS Origins: {settings.CORS_ALLOWED_ORIGINS if hasattr(settings, 'CORS_ALLOWED_ORIGINS') else ['*']}")
    logger.info("=" * 80)
    
    # Create Socket.IO app
    app = create_socketio_app()
    
    # Run server
    try:
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level="info",
            access_log=True,
            use_colors=True,
        )
    except KeyboardInterrupt:
        logger.info("\n🛑 Shutting down Socket.IO server...")
    except Exception as e:
        logger.error(f"❌ Server error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
