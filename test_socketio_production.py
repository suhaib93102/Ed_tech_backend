#!/usr/bin/env python3
"""
Production Socket.IO Testing Script
Tests Socket.IO connection and real-time features
"""

import socketio
import asyncio
import json
import time
import sys
import requests
from concurrent.futures import ThreadPoolExecutor

# Configuration
SERVER_URL = "http://localhost:8003"
SOCKET_URL = SERVER_URL

class SocketIOTester:
    def __init__(self):
        self.results = []
        self.sio = None

    def log(self, message, status="INFO"):
        """Log test results"""
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] {status}: {message}")
        self.results.append({
            "timestamp": timestamp,
            "status": status,
            "message": message
        })

    async def test_socketio_connection(self):
        """Test basic Socket.IO connection"""
        self.log("Testing Socket.IO connection...")

        try:
            # Create Socket.IO client
            self.sio = socketio.AsyncClient()

            # Set up event handlers
            @self.sio.event
            async def connect():
                self.log("✅ Socket.IO client connected", "SUCCESS")

            @self.sio.event
            async def disconnect():
                self.log("🔌 Socket.IO client disconnected")

            @self.sio.event
            async def connected(data):
                self.log(f"✅ Server acknowledged connection: {data}", "SUCCESS")

            @self.sio.event
            async def error(data):
                self.log(f"❌ Socket.IO error: {data}", "ERROR")

            # Connect to server
            await self.sio.connect(
                SOCKET_URL,
                transports=['polling'],
                wait_timeout=10
            )

            # Wait for connection to establish
            await asyncio.sleep(2)

            if self.sio.connected:
                self.log("✅ Socket.IO connection successful", "SUCCESS")
                return True
            else:
                self.log("❌ Socket.IO connection failed", "ERROR")
                return False

        except Exception as e:
            self.log(f"❌ Socket.IO connection error: {str(e)}", "ERROR")
            return False

    async def test_heartbeat(self):
        """Test heartbeat functionality"""
        if not self.sio or not self.sio.connected:
            self.log("⚠️ Skipping heartbeat test - not connected", "WARNING")
            return False

        self.log("Testing heartbeat functionality...")

        try:
            # Set up heartbeat handler
            heartbeat_received = False

            @self.sio.event
            async def heartbeat_ack(data):
                nonlocal heartbeat_received
                heartbeat_received = True
                self.log(f"✅ Heartbeat acknowledged: {data}", "SUCCESS")

            # Send heartbeat
            await self.sio.emit('heartbeat', {
                'client_time': time.time()
            })

            # Wait for response
            await asyncio.sleep(2)

            if heartbeat_received:
                self.log("✅ Heartbeat test passed", "SUCCESS")
                return True
            else:
                self.log("❌ Heartbeat test failed - no response", "ERROR")
                return False

        except Exception as e:
            self.log(f"❌ Heartbeat test error: {str(e)}", "ERROR")
            return False

    async def test_pair_quiz_session(self):
        """Test pair quiz session creation and joining"""
        if not self.sio or not self.sio.connected:
            self.log("⚠️ Skipping pair quiz test - not connected", "WARNING")
            return False

        self.log("Testing pair quiz session...")

        try:
            # First create a session via REST API
            session_data = {
                "quizConfig": {
                    "subject": "physics",
                    "difficulty": "medium",
                    "numQuestions": 5
                },
                "sessionCode": "TEST123"
            }

            response = requests.post(f"{SERVER_URL}/api/pair-quiz/create/", json=session_data)
            if response.status_code != 201:
                self.log(f"❌ Failed to create session: {response.status_code}", "ERROR")
                return False

            session_result = response.json()
            session_id = session_result.get('sessionId')
            if not session_id:
                self.log("❌ No session ID in response", "ERROR")
                return False

            self.log(f"✅ Created session: {session_id}", "SUCCESS")

            # Now test joining via Socket.IO
            join_received = False
            error_received = None

            @self.sio.event
            async def session_joined(data):
                nonlocal join_received
                join_received = True
                self.log(f"✅ Session joined: {data}", "SUCCESS")

            @self.sio.event
            async def error(data):
                nonlocal error_received
                error_received = data
                self.log(f"❌ Join error: {data}", "ERROR")

            # Join session
            await self.sio.emit('join_session', {
                'sessionId': session_id,
                'userId': 'test-user-1'
            })

            # Wait for response
            await asyncio.sleep(3)

            if join_received:
                self.log("✅ Pair quiz session test passed", "SUCCESS")
                return True
            elif error_received:
                self.log(f"❌ Pair quiz session test failed: {error_received}", "ERROR")
                return False
            else:
                self.log("❌ Pair quiz session test failed - no response", "ERROR")
                return False

        except Exception as e:
            self.log(f"❌ Pair quiz test error: {str(e)}", "ERROR")
            return False

    async def test_metrics(self):
        """Test metrics endpoint"""
        if not self.sio or not self.sio.connected:
            self.log("⚠️ Skipping metrics test - not connected", "WARNING")
            return False

        self.log("Testing metrics endpoint...")

        try:
            metrics_received = False

            @self.sio.event
            async def metrics(data):
                nonlocal metrics_received
                metrics_received = True
                self.log(f"✅ Metrics received: {json.dumps(data, indent=2)}", "SUCCESS")

            # Request metrics
            await self.sio.emit('get_metrics', {})

            # Wait for response
            await asyncio.sleep(2)

            if metrics_received:
                self.log("✅ Metrics test passed", "SUCCESS")
                return True
            else:
                self.log("❌ Metrics test failed - no response", "ERROR")
                return False

        except Exception as e:
            self.log(f"❌ Metrics test error: {str(e)}", "ERROR")
            return False

    async def cleanup(self):
        """Clean up connections"""
        if self.sio and self.sio.connected:
            await self.sio.disconnect()
            self.log("🧹 Cleaned up Socket.IO connection")

    async def run_all_tests(self):
        """Run all Socket.IO tests"""
        print("=" * 80)
        print("🔌 SOCKET.IO PRODUCTION TESTING SUITE")
        print("=" * 80)

        # First check if server is running
        try:
            response = requests.get(f"{SERVER_URL}/api/health/", timeout=5)
            if response.status_code != 200:
                self.log("❌ Server not responding", "ERROR")
                return False
        except:
            self.log("❌ Cannot connect to server", "ERROR")
            return False

        tests = [
            ("Basic Connection", self.test_socketio_connection),
            ("Heartbeat", self.test_heartbeat),
            ("Pair Quiz Session", self.test_pair_quiz_session),
            ("Metrics", self.test_metrics),
        ]

        passed = 0
        total = len(tests)

        try:
            for test_name, test_func in tests:
                print(f"\n🔍 Running: {test_name}")
                print("-" * 50)
                if await test_func():
                    passed += 1
                time.sleep(0.5)  # Small delay between tests
        finally:
            await self.cleanup()

        # Summary
        print("\n" + "=" * 80)
        print("📊 SOCKET.IO TEST RESULTS SUMMARY")
        print("=" * 80)
        print(f"✅ Passed: {passed}/{total}")
        print(f"❌ Failed: {total - passed}/{total}")
        print(".1f")

        if passed == total:
            print("🎉 ALL SOCKET.IO TESTS PASSED!")
            print("✅ Production Socket.IO server is working correctly")
        elif passed >= total * 0.75:
            print("👍 MOST SOCKET.IO TESTS PASSED!")
        else:
            print("⚠️ SOCKET.IO TESTS FAILED - CHECK SERVER CONFIGURATION")

        print("=" * 80)

        return passed == total


async def main():
    """Main test runner"""
    tester = SocketIOTester()
    success = await tester.run_all_tests()

    # Save results to file
    results_file = "/Users/vishaljha/Desktop/Government-welfare-Schemes/backend/socketio_test_results.json"
    with open(results_file, 'w') as f:
        json.dump(tester.results, f, indent=2)

    print(f"\n📄 Detailed results saved to: {results_file}")

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())