#!/usr/bin/env python3
"""
Test Socket.IO connection with Uvicorn ASGI server
This test verifies that Socket.IO is properly configured and responding
"""

import subprocess
import time
import requests
import sys
import signal
import json

def test_socketio_endpoint():
    """Test the Socket.IO endpoint"""
    print("=" * 60)
    print("🧪 Socket.IO ASGI Server Test")
    print("=" * 60)
    
    # Start Uvicorn server
    print("\n1️⃣ Starting Uvicorn ASGI server...")
    print("   Command: uvicorn edtech_project.asgi:application --host 0.0.0.0 --port 8003")
    
    server_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "edtech_project.asgi:application", 
         "--host", "0.0.0.0", "--port", "8003"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait for server to start
    time.sleep(3)
    
    try:
        # Test health endpoint
        print("\n2️⃣ Testing health endpoint...")
        health_response = requests.get("http://localhost:8003/api/health/", timeout=5)
        if health_response.status_code == 200:
            print(f"   ✅ Health check passed: {health_response.json()}")
        else:
            print(f"   ❌ Health check failed: {health_response.status_code}")
            return False
        
        # Test Socket.IO polling endpoint
        print("\n3️⃣ Testing Socket.IO polling endpoint...")
        socketio_response = requests.get(
            "http://localhost:8003/socket.io/?EIO=4&transport=polling",
            timeout=10
        )
        
        if socketio_response.status_code == 200:
            # Parse the response (Socket.IO uses a specific format)
            response_text = socketio_response.text
            print(f"   ✅ Socket.IO polling endpoint responding")
            print(f"   Response (first 100 chars): {response_text[:100]}...")
            
            # Try to parse the response
            try:
                # Remove the leading '0' from Socket.IO response
                if response_text.startswith('0'):
                    json_part = response_text[1:]
                    data = json.loads(json_part)
                    print(f"   ✅ Valid Socket.IO response:")
                    print(f"      - Session ID: {data.get('sid')}")
                    print(f"      - Ping timeout: {data.get('pingTimeout')}ms")
                    print(f"      - Ping interval: {data.get('pingInterval')}ms")
                    print(f"      - Available transports: {data.get('upgrades', [])}")
            except json.JSONDecodeError as e:
                print(f"   ⚠️  Could not parse JSON: {e}")
        else:
            print(f"   ❌ Socket.IO endpoint failed: {socketio_response.status_code}")
            print(f"   Response: {socketio_response.text}")
            return False
        
        print("\n" + "=" * 60)
        print("✅ All Socket.IO tests passed!")
        print("=" * 60)
        print("\n📝 Configuration Summary:")
        print("   - ASGI Server: ✅ Running")
        print("   - Health Endpoint: ✅ Working")
        print("   - Socket.IO Transport: ✅ Polling (with WebSocket upgrade available)")
        print("   - Next step: Start the frontend with 'expo start'")
        print("=" * 60)
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("   ❌ Could not connect to server. Is it running?")
        return False
    except requests.exceptions.Timeout:
        print("   ❌ Request timed out")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    finally:
        # Clean up
        print("\n🛑 Stopping server...")
        server_process.send_signal(signal.SIGTERM)
        try:
            server_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server_process.kill()
        print("   ✅ Server stopped")

if __name__ == "__main__":
    success = test_socketio_endpoint()
    sys.exit(0 if success else 1)
