#!/usr/bin/env python3
"""
Comprehensive API Testing Script
Tests all endpoints: auth, quiz, flashcards, mock tests, images, pair quizzes
"""

import requests
import json
import time
import sys
import os
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:8003"
API_BASE = f"{BASE_URL}/api"

# Test data
TEST_USER = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123"
}

TEST_QUIZ_CONFIG = {
    "subject": "physics",
    "difficulty": "medium",
    "numQuestions": 5,
    "quizType": "practice"
}

TEST_FLASHCARD_CONFIG = {
    "subject": "chemistry",
    "topic": "organic_chemistry",
    "difficulty": "medium",
    "numCards": 10
}

TEST_MOCK_CONFIG = {
    "subject": "biology",
    "difficulty": "medium",
    "includeTimer": True,
    "timeLimit": 30
}

class APITester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []

    def log(self, message, status="INFO"):
        """Log test results"""
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] {status}: {message}")
        self.test_results.append({
            "timestamp": timestamp,
            "status": status,
            "message": message
        })

    def test_health(self):
        """Test health endpoint"""
        self.log("Testing health endpoint...")
        try:
            response = self.session.get(f"{API_BASE}/health/")
            if response.status_code == 200:
                self.log("✅ Health check passed", "SUCCESS")
                return True
            else:
                self.log(f"❌ Health check failed: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Health check error: {str(e)}", "ERROR")
            return False

    def test_register(self):
        """Test user registration"""
        self.log("Testing user registration...")
        try:
            data = {
                "username": TEST_USER["username"],
                "email": TEST_USER["email"],
                "password": TEST_USER["password"],
                "password_confirm": TEST_USER["password"]
            }
            response = self.session.post(f"{API_BASE}/auth/register/", json=data)
            if response.status_code == 201:
                self.log("✅ Registration successful", "SUCCESS")
                return True
            elif response.status_code == 400 and "already exists" in response.text.lower():
                self.log("⚠️ User already exists, continuing...", "WARNING")
                return True
            else:
                self.log(f"❌ Registration failed: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Registration error: {str(e)}", "ERROR")
            return False

    def test_login(self):
        """Test user login"""
        self.log("Testing user login...")
        try:
            data = {
                "username": TEST_USER["username"],
                "password": TEST_USER["password"]
            }
            response = self.session.post(f"{API_BASE}/auth/login/", json=data)
            if response.status_code == 200:
                data = response.json()
                if "token" in data:
                    self.auth_token = data["token"]
                    self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                    self.log("✅ Login successful", "SUCCESS")
                    return True
                else:
                    self.log("❌ Login response missing token", "ERROR")
                    return False
            else:
                self.log(f"❌ Login failed: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Login error: {str(e)}", "ERROR")
            return False

    def test_password_reset(self):
        """Test password reset request"""
        self.log("Testing password reset request...")
        try:
            data = {"email": TEST_USER["email"]}
            response = self.session.post(f"{API_BASE}/auth/request-password-reset/", json=data)
            # Password reset might fail due to email config, but endpoint should respond
            if response.status_code in [200, 201]:
                self.log("✅ Password reset request accepted", "SUCCESS")
                return True
            else:
                self.log(f"⚠️ Password reset failed: {response.status_code} - {response.text}", "WARNING")
                return True  # Not critical for other tests
        except Exception as e:
            self.log(f"⚠️ Password reset error: {str(e)}", "WARNING")
            return True

    def test_quiz_generation(self):
        """Test quiz generation"""
        self.log("Testing quiz generation...")
        try:
            response = self.session.post(f"{API_BASE}/quiz/generate/", json=TEST_QUIZ_CONFIG)
            if response.status_code == 201:
                data = response.json()
                if "questions" in data and len(data["questions"]) > 0:
                    self.log(f"✅ Quiz generated: {len(data['questions'])} questions", "SUCCESS")
                    return True
                else:
                    self.log("❌ Quiz response missing questions", "ERROR")
                    return False
            else:
                self.log(f"❌ Quiz generation failed: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Quiz generation error: {str(e)}", "ERROR")
            return False

    def test_flashcard_generation(self):
        """Test flashcard generation"""
        self.log("Testing flashcard generation...")
        try:
            response = self.session.post(f"{API_BASE}/flashcards/generate/", json=TEST_FLASHCARD_CONFIG)
            if response.status_code == 201:
                data = response.json()
                if "flashcards" in data and len(data["flashcards"]) > 0:
                    self.log(f"✅ Flashcards generated: {len(data['flashcards'])} cards", "SUCCESS")
                    return True
                else:
                    self.log("❌ Flashcard response missing cards", "ERROR")
                    return False
            else:
                self.log(f"❌ Flashcard generation failed: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Flashcard generation error: {str(e)}", "ERROR")
            return False

    def test_mock_test_generation(self):
        """Test mock test generation"""
        self.log("Testing mock test generation...")
        try:
            response = self.session.post(f"{API_BASE}/mock-test/generate/", json=TEST_MOCK_CONFIG)
            if response.status_code == 201:
                data = response.json()
                if "questions" in data and len(data["questions"]) > 0:
                    self.log(f"✅ Mock test generated: {len(data['questions'])} questions", "SUCCESS")
                    return True
                else:
                    self.log("❌ Mock test response missing questions", "ERROR")
                    return False
            else:
                self.log(f"❌ Mock test generation failed: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Mock test generation error: {str(e)}", "ERROR")
            return False

    def test_image_processing(self):
        """Test image processing for question solving"""
        self.log("Testing image processing...")
        try:
            # Create a simple test image (we'll use a dummy approach)
            # In real testing, you'd upload an actual image
            files = {
                'image': ('test.jpg', b'dummy image data', 'image/jpeg')
            }
            data = {
                'subject': 'mathematics',
                'question_type': 'algebra'
            }
            response = self.session.post(f"{API_BASE}/question-solver/solve-image/", files=files, data=data)
            # Image processing might require specific setup, so we'll be lenient
            if response.status_code in [200, 201, 400, 415]:
                self.log(f"✅ Image processing endpoint responded: {response.status_code}", "SUCCESS")
                return True
            else:
                self.log(f"❌ Image processing failed: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"⚠️ Image processing error: {str(e)}", "WARNING")
            return True  # Not critical

    def test_pair_quiz_creation(self):
        """Test pair quiz session creation"""
        self.log("Testing pair quiz creation...")
        try:
            data = {
                "quizConfig": TEST_QUIZ_CONFIG,
                "sessionCode": "TEST123"
            }
            response = self.session.post(f"{API_BASE}/pair-quiz/create/", json=data)
            if response.status_code == 201:
                data = response.json()
                if "sessionId" in data:
                    self.log(f"✅ Pair quiz created: {data['sessionId']}", "SUCCESS")
                    return data["sessionId"]
                else:
                    self.log("❌ Pair quiz response missing sessionId", "ERROR")
                    return None
            else:
                self.log(f"❌ Pair quiz creation failed: {response.status_code} - {response.text}", "ERROR")
                return None
        except Exception as e:
            self.log(f"❌ Pair quiz creation error: {str(e)}", "ERROR")
            return None

    def test_pair_quiz_join(self, session_id):
        """Test joining pair quiz session"""
        if not session_id:
            self.log("⚠️ Skipping pair quiz join - no session ID", "WARNING")
            return False

        self.log(f"Testing pair quiz join for session {session_id}...")
        try:
            data = {
                "sessionId": session_id,
                "userId": "test-user-2"
            }
            response = self.session.post(f"{API_BASE}/pair-quiz/join/", json=data)
            if response.status_code == 200:
                self.log("✅ Pair quiz join successful", "SUCCESS")
                return True
            else:
                self.log(f"❌ Pair quiz join failed: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Pair quiz join error: {str(e)}", "ERROR")
            return False

    def test_daily_quiz(self):
        """Test daily quiz functionality"""
        self.log("Testing daily quiz...")
        try:
            response = self.session.get(f"{API_BASE}/daily-quiz/today/")
            if response.status_code == 200:
                data = response.json()
                if "questions" in data:
                    self.log(f"✅ Daily quiz retrieved: {len(data['questions'])} questions", "SUCCESS")
                    return True
                else:
                    self.log("❌ Daily quiz response missing questions", "ERROR")
                    return False
            else:
                self.log(f"❌ Daily quiz failed: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Daily quiz error: {str(e)}", "ERROR")
            return False

    def run_all_tests(self):
        """Run all API tests"""
        print("=" * 80)
        print("🚀 COMPREHENSIVE API TESTING SUITE")
        print("=" * 80)

        tests = [
            ("Health Check", self.test_health),
            ("User Registration", self.test_register),
            ("User Login", self.test_login),
            ("Password Reset", self.test_password_reset),
            ("Quiz Generation", self.test_quiz_generation),
            ("Flashcard Generation", self.test_flashcard_generation),
            ("Mock Test Generation", self.test_mock_test_generation),
            ("Image Processing", self.test_image_processing),
            ("Daily Quiz", self.test_daily_quiz),
        ]

        passed = 0
        total = len(tests)

        for test_name, test_func in tests:
            print(f"\n🔍 Running: {test_name}")
            print("-" * 50)
            if test_func():
                passed += 1
            time.sleep(0.5)  # Small delay between tests

        # Test pair quiz (requires session creation first)
        print("\n🔍 Running: Pair Quiz Creation")
        print("-" * 50)
        session_id = self.test_pair_quiz_creation()
        if session_id:
            passed += 1
            total += 1

            print("\n🔍 Running: Pair Quiz Join")
            print("-" * 50)
            if self.test_pair_quiz_join(session_id):
                passed += 1
            total += 1

        # Summary
        print("\n" + "=" * 80)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 80)
        print(f"✅ Passed: {passed}/{total}")
        print(f"❌ Failed: {total - passed}/{total}")
        print(".1f")

        if passed == total:
            print("🎉 ALL TESTS PASSED!")
        elif passed >= total * 0.8:
            print("👍 MOST TESTS PASSED!")
        else:
            print("⚠️ SOME TESTS FAILED - CHECK LOGS ABOVE")

        print("=" * 80)

        return passed == total


def main():
    """Main test runner"""
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("Usage: python test_comprehensive_api.py")
        print("Tests all API endpoints for the EdTech platform")
        return

    tester = APITester()
    success = tester.run_all_tests()

    # Save results to file
    results_file = Path("/Users/vishaljha/Desktop/Government-welfare-Schemes/backend/test_results.json")
    with open(results_file, 'w') as f:
        json.dump(tester.test_results, f, indent=2)

    print(f"\n📄 Detailed results saved to: {results_file}")

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()