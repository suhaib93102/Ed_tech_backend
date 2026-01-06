#!/bin/bash

# Simple Feature Testing Script with Curl Commands
# Tests all 10 features + auth endpoints

set -e

API_URL="http://localhost:8001"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "========================================="
echo "TESTING ALL FEATURES - $TIMESTAMP"
echo "========================================="

# PHASE 1: User Registration
echo ""
echo "1. TESTING USER REGISTRATION"
echo "----------------------------"
REGISTER_RESPONSE=$(curl -s -X POST "$API_URL/api/auth/register/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser_'$TIMESTAMP'@example.com",
    "password": "TestPassword123!",
    "username": "testuser_'$TIMESTAMP'",
    "name": "Test User"
  }')

echo "$REGISTER_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$REGISTER_RESPONSE"

# Extract token
TOKEN=$(echo "$REGISTER_RESPONSE" | grep -o '"token":"[^"]*' | cut -d'"' -f4)
echo "Token: $TOKEN"

# PHASE 2: Test Login
echo ""
echo "2. TESTING USER LOGIN"
echo "----------------------------"
LOGIN_RESPONSE=$(curl -s -X POST "$API_URL/api/auth/login/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser_'$TIMESTAMP'@example.com",
    "password": "TestPassword123!"
  }')

echo "$LOGIN_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$LOGIN_RESPONSE"

# PHASE 3: Test Quiz Feature
echo ""
echo "3. TESTING QUIZ FEATURE"
echo "----------------------------"
QUIZ_RESPONSE=$(curl -s -X POST "$API_URL/api/quiz/generate/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "subject": "Mathematics",
    "difficulty": "medium",
    "num_questions": 5
  }')

echo "$QUIZ_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$QUIZ_RESPONSE"

# PHASE 4: Test Mock Test Feature
echo ""
echo "4. TESTING MOCK TEST FEATURE"
echo "----------------------------"
MOCK_TEST_RESPONSE=$(curl -s -X POST "$API_URL/api/quiz/create/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "exam_type": "JEE",
    "duration": 180
  }')

echo "$MOCK_TEST_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$MOCK_TEST_RESPONSE"

# PHASE 5: Test Flashcards Feature
echo ""
echo "5. TESTING FLASHCARDS FEATURE"
echo "----------------------------"
FLASHCARDS_RESPONSE=$(curl -s -X POST "$API_URL/api/flashcards/generate/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "topic": "Algebra",
    "count": 10
  }')

echo "$FLASHCARDS_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$FLASHCARDS_RESPONSE"

# PHASE 6: Test Pair Quiz Feature
echo ""
echo "6. TESTING PAIR QUIZ FEATURE"
echo "----------------------------"
PAIR_QUIZ_RESPONSE=$(curl -s -X POST "$API_URL/api/pair-quiz/create/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "question_count": 5
  }')

echo "$PAIR_QUIZ_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$PAIR_QUIZ_RESPONSE"

# PHASE 7: Test Predicted Questions Feature
echo ""
echo "7. TESTING PREDICTED QUESTIONS FEATURE"
echo "----------------------------"
PREDICTED_RESPONSE=$(curl -s -X POST "$API_URL/api/predicted-questions/generate/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "exam": "JEE_MAIN",
    "topic": "Thermodynamics"
  }')

echo "$PREDICTED_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$PREDICTED_RESPONSE"

# PHASE 8: Test Ask Question Feature
echo ""
echo "8. TESTING ASK QUESTION FEATURE"
echo "----------------------------"
ASK_QUESTION_RESPONSE=$(curl -s -X POST "$API_URL/api/solve/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "question": "How to solve quadratic equations?",
    "subject": "Mathematics"
  }')

echo "$ASK_QUESTION_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$ASK_QUESTION_RESPONSE"

# PHASE 9: Test YouTube Summarizer Feature
echo ""
echo "9. TESTING YOUTUBE SUMMARIZER FEATURE"
echo "----------------------------"
YOUTUBE_RESPONSE=$(curl -s -X POST "$API_URL/api/youtube/summarize/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
  }')

echo "$YOUTUBE_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$YOUTUBE_RESPONSE"

# PHASE 10: Test Daily Quiz Feature
echo ""
echo "10. TESTING DAILY QUIZ FEATURE"
echo "----------------------------"
DAILY_QUIZ_RESPONSE=$(curl -s -X GET "$API_URL/api/daily-quiz/" \
  -H "Authorization: Bearer $TOKEN")

echo "$DAILY_QUIZ_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$DAILY_QUIZ_RESPONSE"

# PHASE 11: Test Forget Password
echo ""
echo "11. TESTING FORGET PASSWORD"
echo "----------------------------"
FORGET_PASSWORD_RESPONSE=$(curl -s -X POST "$API_URL/api/auth/request-password-reset/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser_'$TIMESTAMP'@example.com"
  }')

echo "$FORGET_PASSWORD_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$FORGET_PASSWORD_RESPONSE"

# PHASE 12: Check Subscription Status
echo ""
echo "12. TESTING SUBSCRIPTION STATUS"
echo "----------------------------"
SUBSCRIPTION_RESPONSE=$(curl -s -X GET "$API_URL/api/subscription/status/" \
  -H "Authorization: Bearer $TOKEN")

echo "$SUBSCRIPTION_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$SUBSCRIPTION_RESPONSE"

# PHASE 13: Get Usage Dashboard
echo ""
echo "13. TESTING USAGE DASHBOARD"
echo "----------------------------"
USAGE_DASHBOARD_RESPONSE=$(curl -s -X GET "$API_URL/api/usage/dashboard/" \
  -H "Authorization: Bearer $TOKEN")

echo "$USAGE_DASHBOARD_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$USAGE_DASHBOARD_RESPONSE"

# PHASE 14: Test Plan Upgrade to BASIC
echo ""
echo "14. TESTING UPGRADE TO BASIC PLAN"
echo "----------------------------"
UPGRADE_BASIC_RESPONSE=$(curl -s -X POST "$API_URL/api/subscription/upgrade/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "plan_id": 2
  }')

echo "$UPGRADE_BASIC_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$UPGRADE_BASIC_RESPONSE"

# PHASE 15: Test Plan Upgrade to PREMIUM
echo ""
echo "15. TESTING UPGRADE TO PREMIUM PLAN"
echo "----------------------------"
UPGRADE_PREMIUM_RESPONSE=$(curl -s -X POST "$API_URL/api/subscription/upgrade/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "plan_id": 3
  }')

echo "$UPGRADE_PREMIUM_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$UPGRADE_PREMIUM_RESPONSE"

echo ""
echo "========================================="
echo "ALL TESTS COMPLETED - $TIMESTAMP"
echo "========================================="
