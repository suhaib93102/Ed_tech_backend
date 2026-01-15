#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

BASE_URL="http://127.0.0.1:8000/api"
USERNAME="testuser"
PASSWORD="testpass123"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Unity Ads Integration - API Testing${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Get CSRF token from login page
echo -e "${BLUE}1️⃣  Getting authentication token...${NC}"
AUTH_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login/" \
  -H "Content-Type: application/json" \
  -d "{\"username\": \"$USERNAME\", \"password\": \"$PASSWORD\"}")

echo "Response: $AUTH_RESPONSE"
TOKEN=$(echo $AUTH_RESPONSE | grep -o '"token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
  echo -e "${RED}❌ Failed to get authentication token${NC}"
  echo "Make sure to login first or use Django session authentication"
  
  # Try to get session cookie
  echo -e "\n${BLUE}Attempting session-based auth...${NC}"
  curl -c /tmp/cookies.txt -X POST "$BASE_URL/auth/login/" \
    -H "Content-Type: application/json" \
    -d "{\"username\": \"$USERNAME\", \"password\": \"$PASSWORD\"}" \
    2>/dev/null | head -20
    
  TOKEN="session"
else
  echo -e "${GREEN}✅ Token obtained: ${TOKEN:0:20}...${NC}\n"
fi

# Test 1: Check if ad should be shown
echo -e "${BLUE}2️⃣  Testing: Check if ad should be shown${NC}"
echo -e "POST /ads/check-should-show-ad/\n"

if [ "$TOKEN" = "session" ]; then
  RESPONSE=$(curl -s -b /tmp/cookies.txt -X POST "$BASE_URL/ads/check-should-show-ad/" \
    -H "Content-Type: application/json" \
    -d '{"feature_name": "daily_quiz", "platform": "ios"}')
else
  RESPONSE=$(curl -s -X POST "$BASE_URL/ads/check-should-show-ad/" \
    -H "Content-Type: application/json" \
    -H "Authorization: Token $TOKEN" \
    -d '{"feature_name": "daily_quiz", "platform": "ios"}')
fi

echo "$RESPONSE" | python -m json.tool 2>/dev/null || echo "$RESPONSE"
echo ""

# Test 2: Log ad impression (SHOWN)
echo -e "${BLUE}3️⃣  Testing: Log ad impression (SHOWN)${NC}"
echo -e "POST /ads/log-impression/\n"

if [ "$TOKEN" = "session" ]; then
  RESPONSE=$(curl -s -b /tmp/cookies.txt -X POST "$BASE_URL/ads/log-impression/" \
    -H "Content-Type: application/json" \
    -d '{"feature_name": "daily_quiz", "ad_type": "interstitial", "platform": "ios", "status": "shown"}')
else
  RESPONSE=$(curl -s -X POST "$BASE_URL/ads/log-impression/" \
    -H "Content-Type: application/json" \
    -H "Authorization: Token $TOKEN" \
    -d '{"feature_name": "daily_quiz", "ad_type": "interstitial", "platform": "ios", "status": "shown"}')
fi

echo "$RESPONSE" | python -m json.tool 2>/dev/null || echo "$RESPONSE"
echo ""

# Test 3: Log ad impression (CLICKED)
echo -e "${BLUE}4️⃣  Testing: Log ad impression (CLICKED)${NC}"
echo -e "POST /ads/log-impression/\n"

if [ "$TOKEN" = "session" ]; then
  RESPONSE=$(curl -s -b /tmp/cookies.txt -X POST "$BASE_URL/ads/log-impression/" \
    -H "Content-Type: application/json" \
    -d '{"feature_name": "daily_quiz", "ad_type": "interstitial", "platform": "ios", "status": "clicked"}')
else
  RESPONSE=$(curl -s -X POST "$BASE_URL/ads/log-impression/" \
    -H "Content-Type: application/json" \
    -H "Authorization: Token $TOKEN" \
    -d '{"feature_name": "daily_quiz", "ad_type": "interstitial", "platform": "ios", "status": "clicked"}')
fi

echo "$RESPONSE" | python -m json.tool 2>/dev/null || echo "$RESPONSE"
echo ""

# Test 4: Log ad impression (CLOSED)
echo -e "${BLUE}5️⃣  Testing: Log ad impression (CLOSED)${NC}"
echo -e "POST /ads/log-impression/\n"

if [ "$TOKEN" = "session" ]; then
  RESPONSE=$(curl -s -b /tmp/cookies.txt -X POST "$BASE_URL/ads/log-impression/" \
    -H "Content-Type: application/json" \
    -d '{"feature_name": "daily_quiz", "ad_type": "interstitial", "platform": "ios", "status": "closed"}')
else
  RESPONSE=$(curl -s -X POST "$BASE_URL/ads/log-impression/" \
    -H "Content-Type: application/json" \
    -H "Authorization: Token $TOKEN" \
    -d '{"feature_name": "daily_quiz", "ad_type": "interstitial", "platform": "ios", "status": "closed"}')
fi

echo "$RESPONSE" | python -m json.tool 2>/dev/null || echo "$RESPONSE"
echo ""

# Test 5: Get user ad stats
echo -e "${BLUE}6️⃣  Testing: Get user ad stats${NC}"
echo -e "GET /ads/user-stats/\n"

if [ "$TOKEN" = "session" ]; then
  RESPONSE=$(curl -s -b /tmp/cookies.txt -X GET "$BASE_URL/ads/user-stats/" \
    -H "Content-Type: application/json")
else
  RESPONSE=$(curl -s -X GET "$BASE_URL/ads/user-stats/" \
    -H "Content-Type: application/json" \
    -H "Authorization: Token $TOKEN")
fi

echo "$RESPONSE" | python -m json.tool 2>/dev/null || echo "$RESPONSE"
echo ""

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ All tests completed!${NC}"
echo -e "${GREEN}========================================${NC}"
