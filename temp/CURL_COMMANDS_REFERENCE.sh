#!/bin/bash

###############################################################################
# CURL COMMAND REFERENCE - All Features, Auth, Usage Tracking
# Database: Supabase PostgreSQL
# Updated: January 6, 2026
###############################################################################

# ==============================================================================
# SETUP VARIABLES
# ==============================================================================

API_BASE_URL="http://localhost:8000"
SUPABASE_URL="postgresql://postgres.vuuitrhrnlhvtfssgikl:54G7qr8faBFuXvqK@aws-1-ap-southeast-1.pooler.supabase.com:5432/postgres"

# Test user credentials
TEST_EMAIL="testuser_$(date +%s)@edtech.com"
TEST_PASSWORD="TestPassword123!"
TEST_USERNAME="testuser_$(date +%s)"

# Will be populated after login
AUTH_TOKEN=""

# ==============================================================================
# SECTION 1: AUTHENTICATION - SIGNUP, LOGIN, PASSWORD RESET
# ==============================================================================

echo "
╔════════════════════════════════════════════════════════════════════════╗
║           SECTION 1: AUTHENTICATION (SIGNUP, LOGIN, PASSWORD)          ║
╚════════════════════════════════════════════════════════════════════════╝
"

# 1.1 SIGNUP - Create new user
echo "[1.1] SIGNUP - Register new user"
echo "Command:"
echo "curl -X POST http://localhost:8000/api/auth/register/ \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{
    \"email\": \"testuser@edtech.com\",
    \"password\": \"TestPassword123!\",
    \"username\": \"testuser\"
  }'"

echo ""
echo "Example execution:"
SIGNUP_RESPONSE=$(curl -s -X POST "$API_BASE_URL/api/auth/register/" \
  -H 'Content-Type: application/json' \
  -d "{
    \"email\": \"$TEST_EMAIL\",
    \"password\": \"$TEST_PASSWORD\",
    \"username\": \"$TEST_USERNAME\"
  }")

echo "$SIGNUP_RESPONSE" | jq '.'
echo ""

# Extract user ID
USER_ID=$(echo "$SIGNUP_RESPONSE" | jq -r '.user_id // empty')
echo "✅ User registered - ID: $USER_ID, Email: $TEST_EMAIL"
echo ""

# 1.2 LOGIN - Get JWT tokens
echo "[1.2] LOGIN - Authenticate and get JWT tokens"
echo "Command:"
echo "curl -X POST http://localhost:8000/api/auth/login/ \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{
    \"email\": \"testuser@edtech.com\",
    \"password\": \"TestPassword123!\"
  }'"

echo ""
echo "Example execution:"
LOGIN_RESPONSE=$(curl -s -X POST "$API_BASE_URL/api/auth/login/" \
  -H 'Content-Type: application/json' \
  -d "{
    \"email\": \"$TEST_EMAIL\",
    \"password\": \"$TEST_PASSWORD\"
  }")

echo "$LOGIN_RESPONSE" | jq '.'
echo ""

# Extract tokens
AUTH_TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.access // empty')
REFRESH_TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.refresh // empty')
echo "✅ Login successful"
echo "   Access Token: ${AUTH_TOKEN:0:50}..."
echo "   Refresh Token: ${REFRESH_TOKEN:0:50}..."
echo ""

# 1.3 FORGET PASSWORD - Request reset token
echo "[1.3] FORGET PASSWORD - Request password reset token"
echo "Command:"
echo "curl -X POST http://localhost:8000/api/auth/forgot-password/ \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"email\": \"testuser@edtech.com\"}'"

echo ""
echo "Example execution:"
RESET_REQUEST=$(curl -s -X POST "$API_BASE_URL/api/auth/forgot-password/" \
  -H 'Content-Type: application/json' \
  -d "{\"email\": \"$TEST_EMAIL\"}")

echo "$RESET_REQUEST" | jq '.'
echo ""

RESET_TOKEN=$(echo "$RESET_REQUEST" | jq -r '.token // empty')
echo "✅ Reset token generated"
echo "   Token: ${RESET_TOKEN:0:50}..."
echo ""

# 1.4 RESET PASSWORD - Reset with token
echo "[1.4] RESET PASSWORD - Change password with token"
echo "Command:"
echo "curl -X POST http://localhost:8000/api/auth/reset-password/ \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{
    \"token\": \"<reset_token_from_above>\",
    \"new_password\": \"NewPassword456!\"
  }'"

echo ""
echo "Example execution:"
PASSWORD_RESET=$(curl -s -X POST "$API_BASE_URL/api/auth/reset-password/" \
  -H 'Content-Type: application/json' \
  -d "{
    \"token\": \"$RESET_TOKEN\",
    \"new_password\": \"NewPassword456!\"
  }")

echo "$PASSWORD_RESET" | jq '.'
echo "✅ Password reset completed"
echo ""

# 1.5 REFRESH TOKEN - Get new access token
echo "[1.5] REFRESH TOKEN - Get new access token using refresh token"
echo "Command:"
echo "curl -X POST http://localhost:8000/api/auth/refresh/ \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"refresh\": \"<refresh_token>\"}'"

echo ""
echo "Example execution:"
REFRESH=$(curl -s -X POST "$API_BASE_URL/api/auth/refresh/" \
  -H 'Content-Type: application/json' \
  -d "{\"refresh\": \"$REFRESH_TOKEN\"}")

echo "$REFRESH" | jq '.'
NEW_TOKEN=$(echo "$REFRESH" | jq -r '.access // empty')
if [ -n "$NEW_TOKEN" ]; then
  AUTH_TOKEN="$NEW_TOKEN"
  echo "✅ New access token obtained"
fi
echo ""

# ==============================================================================
# SECTION 2: SUBSCRIPTION MANAGEMENT
# ==============================================================================

echo "
╔════════════════════════════════════════════════════════════════════════╗
║              SECTION 2: SUBSCRIPTION MANAGEMENT                        ║
╚════════════════════════════════════════════════════════════════════════╝
"

# 2.1 SUBSCRIBE TO FREE PLAN
echo "[2.1] SUBSCRIBE - Assign FREE plan"
echo "Command:"
echo "curl -X POST http://localhost:8000/api/subscription/subscribe/ \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -H 'Authorization: Bearer <YOUR_ACCESS_TOKEN>' \\"
echo "  -d '{\"plan_name\": \"free\"}'"

echo ""
echo "Example execution:"
FREE_SUB=$(curl -s -X POST "$API_BASE_URL/api/subscription/subscribe/" \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  -d '{"plan_name": "free"}')

echo "$FREE_SUB" | jq '.'
echo "✅ User subscribed to FREE plan"
echo ""

# 2.2 UPGRADE TO BASIC PLAN
echo "[2.2] UPGRADE - Upgrade to BASIC plan"
echo "Command:"
echo "curl -X POST http://localhost:8000/api/subscription/upgrade/ \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -H 'Authorization: Bearer <YOUR_ACCESS_TOKEN>' \\"
echo "  -d '{\"plan_name\": \"basic\"}'"

echo ""
echo "Example execution:"
BASIC_SUB=$(curl -s -X POST "$API_BASE_URL/api/subscription/upgrade/" \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  -d '{"plan_name": "basic"}')

echo "$BASIC_SUB" | jq '.'
echo "✅ Upgraded to BASIC plan"
echo ""

# 2.3 UPGRADE TO PREMIUM PLAN
echo "[2.3] UPGRADE - Upgrade to PREMIUM plan"
echo "Command:"
echo "curl -X POST http://localhost:8000/api/subscription/upgrade/ \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -H 'Authorization: Bearer <YOUR_ACCESS_TOKEN>' \\"
echo "  -d '{\"plan_name\": \"premium\"}'"

echo ""
echo "Example execution:"
PREMIUM_SUB=$(curl -s -X POST "$API_BASE_URL/api/subscription/upgrade/" \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  -d '{"plan_name": "premium"}')

echo "$PREMIUM_SUB" | jq '.'
echo "✅ Upgraded to PREMIUM plan"
echo ""

# 2.4 GET SUBSCRIPTION INFO
echo "[2.4] GET SUBSCRIPTION - Retrieve current subscription"
echo "Command:"
echo "curl -X GET http://localhost:8000/api/subscription/info/ \\"
echo "  -H 'Authorization: Bearer <YOUR_ACCESS_TOKEN>'"

echo ""
echo "Example execution:"
SUB_INFO=$(curl -s -X GET "$API_BASE_URL/api/subscription/info/" \
  -H "Authorization: Bearer $AUTH_TOKEN")

echo "$SUB_INFO" | jq '.'
echo "✅ Subscription info retrieved"
echo ""

# ==============================================================================
# SECTION 3: ALL 10 FEATURES - CHECK AND USE
# ==============================================================================

echo "
╔════════════════════════════════════════════════════════════════════════╗
║                        SECTION 3: ALL 10 FEATURES                      ║
╚════════════════════════════════════════════════════════════════════════╝
"

# 3.1 QUIZ
echo "[3.1] QUIZ - Question & Answer Feature"
echo "Check availability:"
echo "curl -X GET http://localhost:8000/api/features/quiz/check/ \\"
echo "  -H 'Authorization: Bearer <YOUR_ACCESS_TOKEN>'"
QUIZ_CHECK=$(curl -s -X GET "$API_BASE_URL/api/features/quiz/check/" \
  -H "Authorization: Bearer $AUTH_TOKEN")
echo "$QUIZ_CHECK" | jq '.'

echo ""
echo "Use feature:"
echo "curl -X POST http://localhost:8000/api/features/quiz/use/ \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -H 'Authorization: Bearer <YOUR_ACCESS_TOKEN>' \\"
echo "  -d '{\"quiz_id\": 1}'"
QUIZ_USE=$(curl -s -X POST "$API_BASE_URL/api/features/quiz/use/" \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  -d '{"quiz_id": 1}')
echo "$QUIZ_USE" | jq '.'
echo ""

# 3.2 MOCK TEST
echo "[3.2] MOCK TEST"
echo "curl -X GET http://localhost:8000/api/features/mock_test/check/ \\"
echo "  -H 'Authorization: Bearer <YOUR_ACCESS_TOKEN>'"
curl -s -X GET "$API_BASE_URL/api/features/mock_test/check/" \
  -H "Authorization: Bearer $AUTH_TOKEN" | jq '.'
echo ""

# 3.3 FLASHCARDS
echo "[3.3] FLASHCARDS"
echo "curl -X GET http://localhost:8000/api/features/flashcards/check/ \\"
echo "  -H 'Authorization: Bearer <YOUR_ACCESS_TOKEN>'"
curl -s -X GET "$API_BASE_URL/api/features/flashcards/check/" \
  -H "Authorization: Bearer $AUTH_TOKEN" | jq '.'
echo ""

# 3.4 PAIR QUIZ
echo "[3.4] PAIR QUIZ (Multiplayer)"
echo "curl -X GET http://localhost:8000/api/features/pair_quiz/check/ \\"
echo "  -H 'Authorization: Bearer <YOUR_ACCESS_TOKEN>'"
curl -s -X GET "$API_BASE_URL/api/features/pair_quiz/check/" \
  -H "Authorization: Bearer $AUTH_TOKEN" | jq '.'
echo ""

# 3.5 PREDICTED QUESTIONS
echo "[3.5] PREDICTED QUESTIONS"
echo "curl -X GET http://localhost:8000/api/features/predicted_questions/check/ \\"
echo "  -H 'Authorization: Bearer <YOUR_ACCESS_TOKEN>'"
curl -s -X GET "$API_BASE_URL/api/features/predicted_questions/check/" \
  -H "Authorization: Bearer $AUTH_TOKEN" | jq '.'
echo ""

# 3.6 ASK QUESTION
echo "[3.6] ASK QUESTION"
echo "curl -X POST http://localhost:8000/api/features/ask_question/use/ \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -H 'Authorization: Bearer <YOUR_ACCESS_TOKEN>' \\"
echo "  -d '{\"question\": \"What is machine learning?\"}'"
curl -s -X POST "$API_BASE_URL/api/features/ask_question/use/" \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  -d '{"question": "What is machine learning?"}' | jq '.'
echo ""

# 3.7 YOUTUBE SUMMARIZER
echo "[3.7] YOUTUBE SUMMARIZER"
echo "curl -X GET http://localhost:8000/api/features/youtube_summarizer/check/ \\"
echo "  -H 'Authorization: Bearer <YOUR_ACCESS_TOKEN>'"
curl -s -X GET "$API_BASE_URL/api/features/youtube_summarizer/check/" \
  -H "Authorization: Bearer $AUTH_TOKEN" | jq '.'
echo ""

# 3.8 PYQ (PREVIOUS YEAR QUESTIONS)
echo "[3.8] PYQ - Previous Year Questions"
echo "curl -X GET http://localhost:8000/api/features/pyq_features/check/ \\"
echo "  -H 'Authorization: Bearer <YOUR_ACCESS_TOKEN>'"
curl -s -X GET "$API_BASE_URL/api/features/pyq_features/check/" \
  -H "Authorization: Bearer $AUTH_TOKEN" | jq '.'
echo ""

# 3.9 PREVIOUS PAPERS
echo "[3.9] PREVIOUS PAPERS"
echo "curl -X GET http://localhost:8000/api/features/previous_papers/check/ \\"
echo "  -H 'Authorization: Bearer <YOUR_ACCESS_TOKEN>'"
curl -s -X GET "$API_BASE_URL/api/features/previous_papers/check/" \
  -H "Authorization: Bearer $AUTH_TOKEN" | jq '.'
echo ""

# 3.10 DAILY QUIZ
echo "[3.10] DAILY QUIZ"
echo "curl -X GET http://localhost:8000/api/features/daily_quiz/check/ \\"
echo "  -H 'Authorization: Bearer <YOUR_ACCESS_TOKEN>'"
curl -s -X GET "$API_BASE_URL/api/features/daily_quiz/check/" \
  -H "Authorization: Bearer $AUTH_TOKEN" | jq '.'
echo ""

# ==============================================================================
# SECTION 4: USAGE TRACKING & ANALYTICS
# ==============================================================================

echo "
╔════════════════════════════════════════════════════════════════════════╗
║                    SECTION 4: USAGE TRACKING & ANALYTICS               ║
╚════════════════════════════════════════════════════════════════════════╝
"

# 4.1 USAGE DASHBOARD
echo "[4.1] USAGE DASHBOARD - View all usage"
echo "Command:"
echo "curl -X GET http://localhost:8000/api/usage/dashboard/ \\"
echo "  -H 'Authorization: Bearer <YOUR_ACCESS_TOKEN>'"
echo ""
echo "Response:"
curl -s -X GET "$API_BASE_URL/api/usage/dashboard/" \
  -H "Authorization: Bearer $AUTH_TOKEN" | jq '.'
echo ""

# 4.2 FEATURE USAGE
echo "[4.2] FEATURE USAGE - Get usage for specific feature"
echo "Command:"
echo "curl -X GET http://localhost:8000/api/usage/feature/quiz/ \\"
echo "  -H 'Authorization: Bearer <YOUR_ACCESS_TOKEN>'"
echo ""
echo "Response:"
curl -s -X GET "$API_BASE_URL/api/usage/feature/quiz/" \
  -H "Authorization: Bearer $AUTH_TOKEN" | jq '.'
echo ""

# 4.3 CHECK AVAILABILITY
echo "[4.3] CHECK AVAILABILITY - Check if feature is available"
echo "Command:"
echo "curl -X POST http://localhost:8000/api/usage/check/ \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -H 'Authorization: Bearer <YOUR_ACCESS_TOKEN>' \\"
echo "  -d '{\"feature\": \"quiz\"}'"
echo ""
echo "Response:"
curl -s -X POST "$API_BASE_URL/api/usage/check/" \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  -d '{"feature": "quiz"}' | jq '.'
echo ""

# 4.4 RECORD USAGE
echo "[4.4] RECORD USAGE - Manually record feature usage"
echo "Command:"
echo "curl -X POST http://localhost:8000/api/usage/record/ \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -H 'Authorization: Bearer <YOUR_ACCESS_TOKEN>' \\"
echo "  -d '{\"feature\": \"quiz\", \"success\": true}'"
echo ""
echo "Response:"
curl -s -X POST "$API_BASE_URL/api/usage/record/" \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  -d '{"feature": "quiz", "success": true}' | jq '.'
echo ""

# 4.5 USAGE STATISTICS
echo "[4.5] USAGE STATISTICS - Get detailed stats"
echo "Command:"
echo "curl -X GET http://localhost:8000/api/usage/stats/ \\"
echo "  -H 'Authorization: Bearer <YOUR_ACCESS_TOKEN>'"
echo ""
echo "Response:"
curl -s -X GET "$API_BASE_URL/api/usage/stats/" \
  -H "Authorization: Bearer $AUTH_TOKEN" | jq '.'
echo ""

# 4.6 SUBSCRIPTION INFO
echo "[4.6] SUBSCRIPTION INFO - Get current subscription with limits"
echo "Command:"
echo "curl -X GET http://localhost:8000/api/usage/subscription/ \\"
echo "  -H 'Authorization: Bearer <YOUR_ACCESS_TOKEN>'"
echo ""
echo "Response:"
curl -s -X GET "$API_BASE_URL/api/usage/subscription/" \
  -H "Authorization: Bearer $AUTH_TOKEN" | jq '.'
echo ""

# ==============================================================================
# SECTION 5: ADMIN ENDPOINTS (Pair Quiz Management)
# ==============================================================================

echo "
╔════════════════════════════════════════════════════════════════════════╗
║              SECTION 5: ADMIN - PAIR QUIZ MANAGEMENT                   ║
╚════════════════════════════════════════════════════════════════════════╝
"

# 5.1 GET ALL SESSIONS
echo "[5.1] ADMIN - Get all pair quiz sessions"
echo "Command:"
echo "curl -X GET http://localhost:8000/api/admin/pair-quiz/sessions/ \\"
echo "  -H 'Authorization: Bearer <YOUR_ACCESS_TOKEN>'"
echo ""

# 5.2 SESSION STATISTICS
echo "[5.2] ADMIN - Get session statistics"
echo "Command:"
echo "curl -X GET http://localhost:8000/api/admin/pair-quiz/stats/ \\"
echo "  -H 'Authorization: Bearer <YOUR_ACCESS_TOKEN>'"
echo ""

# 5.3 USER GAME HISTORY
echo "[5.3] ADMIN - Get user's game history"
echo "Command:"
echo "curl -X GET http://localhost:8000/api/admin/users/<user_id>/games/ \\"
echo "  -H 'Authorization: Bearer <YOUR_ACCESS_TOKEN>'"
echo ""

# ==============================================================================
# SECTION 6: QUICK REFERENCE - Common Operations
# ==============================================================================

echo "
╔════════════════════════════════════════════════════════════════════════╗
║            SECTION 6: QUICK REFERENCE - COMMON OPERATIONS              ║
╚════════════════════════════════════════════════════════════════════════╝
"

cat << 'EOF'

1. COMPLETE USER JOURNEY
═════════════════════════════════════════════════════════════════════════

Step 1: Signup
curl -X POST http://localhost:8000/api/auth/register/ \
  -H 'Content-Type: application/json' \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!",
    "username": "testuser"
  }'

Step 2: Login (copy access token from response)
curl -X POST http://localhost:8000/api/auth/login/ \
  -H 'Content-Type: application/json' \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!"
  }'

Step 3: Subscribe to plan
curl -X POST http://localhost:8000/api/subscription/subscribe/ \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer <ACCESS_TOKEN>' \
  -d '{"plan_name": "free"}'

Step 4: Use a feature
curl -X POST http://localhost:8000/api/features/quiz/use/ \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer <ACCESS_TOKEN>' \
  -d '{"quiz_id": 1}'

Step 5: Check usage
curl -X GET http://localhost:8000/api/usage/dashboard/ \
  -H 'Authorization: Bearer <ACCESS_TOKEN>'


2. RESET DATABASE (for testing)
═════════════════════════════════════════════════════════════════════════

# Via Django shell
python manage.py shell
>>> from django.core.management import call_command
>>> call_command('flush', '--noinput')

# Via Supabase
# Log in to Supabase console and delete/truncate tables


3. CHECK SUPABASE CONNECTION
═════════════════════════════════════════════════════════════════════════

python manage.py dbshell

Or via Python:
python << 'EOPP'
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edtech_project.settings')
import django
django.setup()
from django.db import connection
print("Database connected:", connection.get_connection_params())
EOPP


4. VIEW DATABASE CONTENTS
═════════════════════════════════════════════════════════════════════════

# Users
curl -s http://localhost:8000/api/admin/users/ \
  -H 'Authorization: Bearer <ADMIN_TOKEN>' | jq '.'

# Subscriptions
curl -s http://localhost:8000/api/admin/subscriptions/ \
  -H 'Authorization: Bearer <ADMIN_TOKEN>' | jq '.'

# Usage logs
curl -s http://localhost:8000/api/admin/usage-logs/ \
  -H 'Authorization: Bearer <ADMIN_TOKEN>' | jq '.'


5. PERFORMANCE TESTING
═════════════════════════════════════════════════════════════════════════

# Load test multiple requests
for i in {1..100}; do
  curl -s http://localhost:8000/api/usage/dashboard/ \
    -H "Authorization: Bearer <ACCESS_TOKEN>" > /dev/null &
done
wait

# Monitor response time
curl -w "\nTime: %{time_total}s\n" \
  http://localhost:8000/api/usage/dashboard/ \
  -H 'Authorization: Bearer <ACCESS_TOKEN>'

EOF

# ==============================================================================
# SAVE CREDENTIALS FOR REFERENCE
# ==============================================================================

echo "
═════════════════════════════════════════════════════════════════════════
CREDENTIALS SAVED FOR TESTING
═════════════════════════════════════════════════════════════════════════

Email:    $TEST_EMAIL
Password: $TEST_PASSWORD (Original)
Username: $TEST_USERNAME
User ID:  $USER_ID

Access Token:  $AUTH_TOKEN
Refresh Token: $REFRESH_TOKEN

💾 Save these for testing API endpoints
═════════════════════════════════════════════════════════════════════════
"

# Save to file
cat > curl_credentials.json << EOF
{
  "email": "$TEST_EMAIL",
  "password": "$TEST_PASSWORD",
  "username": "$TEST_USERNAME",
  "user_id": "$USER_ID",
  "access_token": "$AUTH_TOKEN",
  "refresh_token": "$REFRESH_TOKEN",
  "api_base_url": "$API_BASE_URL"
}
EOF

echo "✅ Credentials saved to curl_credentials.json"
echo ""
